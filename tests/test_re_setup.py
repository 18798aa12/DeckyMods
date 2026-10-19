import pytest
from decky_mods.errors import ModsError
from decky_mods.re_setup import RESettings, inspect_resident


@pytest.fixture
def setup(tmp_path):
    root = tmp_path / "RE7"
    root.mkdir()
    (root / "dinput8.dll").write_bytes(b"loader")
    (root / "re2_fw_config.txt").write_text(
        "Other_Option=original\nLooseFileLoader_Enabled=false\n"
    )
    game = {
        "id": "residentevil7",
        "series": "resident-evil",
        "name": "RE7",
        "path": str(root),
        "installed": True,
        "adapter": "reframework",
        "app_id": "418370",
        "running": False,
        "build_id": "1",
    }
    return RESettings(tmp_path / "settings"), game, root


def test_resource_setup_preserves_other_settings_and_restores(setup):
    manager, game, root = setup
    before = (root / "re2_fw_config.txt").read_bytes()
    result = manager.apply(game, ["LooseFileLoader_Enabled"])
    assert result["loose_enabled"]
    assert "Other_Option=original" in (root / "re2_fw_config.txt").read_text()
    manager.restore(game)
    assert (root / "re2_fw_config.txt").read_bytes() == before


def test_config_drift_cannot_be_overwritten_by_restore(setup):
    manager, game, root = setup
    manager.apply(game, ["LooseFileLoader_Enabled"])
    path = root / "re2_fw_config.txt"
    path.write_text(path.read_text() + "New_Option=keep\n")
    with pytest.raises(ModsError, match="外部修改"):
        manager.restore(game)
    assert "New_Option=keep" in path.read_text()


def test_config_duplicate_missing_and_busy_are_blocked(setup):
    manager, game, root = setup
    with pytest.raises(ModsError):
        manager.apply({**game, "running": True}, ["LooseFileLoader_Enabled"])
    (root / "re2_fw_config.txt").write_text(
        "LooseFileLoader_Enabled=true\nLooseFileLoader_Enabled=false\n"
    )
    with pytest.raises(ModsError, match="配置"):
        manager.apply(game, ["LooseFileLoader_Enabled"])
    (root / "re2_fw_config.txt").unlink()
    with pytest.raises(ModsError, match="运行一次"):
        manager.apply(game, ["LooseFileLoader_Enabled"])


def test_re9_pak_flags_cannot_be_enabled_on_other_games(setup):
    manager, game, _ = setup
    with pytest.raises(ModsError):
        manager.apply(game, ["IntegrityCheckBypass_LoadPakDirectory"])
    info = manager.apply(
        {**game, "id": "residentevilrequiem"},
        ["LooseFileLoader_Enabled", "IntegrityCheckBypass_LoadPakDirectory"],
    )
    assert info["pak_directory_enabled"]


def test_runtime_report_uses_actual_log_and_does_not_infer_from_dll_strings(setup):
    manager, game, root = setup
    info = inspect_resident(game)
    assert info["runtime_tdb"] is None
    assert info["renderer"] is None
    (root / "re2_framework_log.txt").write_text(
        "TDB Version: 70\nBackBufferRenderer D3D12 initialized\n"
        "[ScriptState] Running script /game/reframework/autorun/ItemUnlocker.lua...\n"
        "Lua state initialized\n"
    )
    info = inspect_resident(game)
    assert info["runtime_tdb"] == 70
    assert info["renderer"] == "D3D12"
    assert info["script_count"] == 1
    assert info["runtime_evidence"]


def test_shared_config_symlink_is_rejected(setup, tmp_path):
    manager, game, root = setup
    outside = tmp_path / "outside"
    outside.write_text("LooseFileLoader_Enabled=false\n")
    (root / "re2_fw_config.txt").unlink()
    (root / "re2_fw_config.txt").symlink_to(outside)
    with pytest.raises(ModsError):
        manager.apply(game, ["LooseFileLoader_Enabled"])
    assert outside.read_text() == "LooseFileLoader_Enabled=false\n"


def test_configuration_edit_during_backup_preserves_external_settings(setup, monkeypatch):
    from decky_mods.gamefs import GameFiles

    manager, game, root = setup
    original = GameFiles.capture

    def concurrently_changed(files, target):
        (root / target).write_text("Other_Option=NEW\nLooseFileLoader_Enabled=false\n")
        return original(files, target)

    monkeypatch.setattr(GameFiles, "capture", concurrently_changed)
    with pytest.raises(ModsError, match="外部修改"):
        manager.apply(game, ["LooseFileLoader_Enabled"])
    assert "Other_Option=NEW" in (root / "re2_fw_config.txt").read_text()


def test_configuration_retries_recover_after_file_written_before_commit(setup):
    manager, game, root = setup
    before = (root / "re2_fw_config.txt").read_bytes()

    def interrupted(index, target):
        raise KeyboardInterrupt("power loss")

    manager.engine.fault = interrupted
    with pytest.raises(KeyboardInterrupt):
        manager.apply(game, ["LooseFileLoader_Enabled"])
    restarted = RESettings(manager.directory)
    restarted.restore(game)
    assert (root / "re2_fw_config.txt").read_bytes() == before
    assert not restarted.engine.db.pending(game["id"])
