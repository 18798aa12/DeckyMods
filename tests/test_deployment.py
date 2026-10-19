from pathlib import Path

import pytest
from decky_mods.deployment import Deployment
from decky_mods.errors import ModsError


@pytest.fixture
def game(tmp_path):
    directory = tmp_path / "Game"
    directory.mkdir()
    (directory / "original.txt").write_bytes(b"vanilla")
    return {"id": "testgame", "path": str(directory), "build_id": "1", "running": False}


def prepare(engine, game, tmp_path, name="one", payload=b"mod", target="original.txt", kind=None):
    source = tmp_path / name
    source.mkdir(exist_ok=True)
    (source / "file.bin").write_bytes(payload)
    mapping = {
        "files": [{"source": "file.bin", "target": target, **({"kind": kind} if kind else {})}],
        "warnings": [],
        "requirements": [],
        "blocked_reason": None,
    }
    return engine.prepare(game, name, source, mapping)


def test_install_conflict_ack_disable_restore_and_uninstall(tmp_path, game):
    engine = Deployment(tmp_path / "state")
    plan = prepare(engine, game, tmp_path)
    assert plan["conflicts"] == ["original.txt"]
    with pytest.raises(ModsError, match="冲突|覆盖"):
        engine.install(game, plan["id"])
    mod = engine.install(game, plan["id"], allow_conflicts=True)
    assert Path(game["path"], "original.txt").read_bytes() == b"mod"
    engine.set_enabled(game, mod["id"], False)
    assert Path(game["path"], "original.txt").read_bytes() == b"vanilla"
    engine.set_enabled(game, mod["id"], True)
    engine.uninstall(game, mod["id"])
    assert Path(game["path"], "original.txt").read_bytes() == b"vanilla"
    assert engine.list_mods(game["id"]) == []


def test_overlapping_mods_restore_lower_enabled_layer(tmp_path, game):
    engine = Deployment(tmp_path / "state")
    one = engine.install(game, prepare(engine, game, tmp_path, "one", b"one")["id"], True)
    two = engine.install(game, prepare(engine, game, tmp_path, "two", b"two")["id"], True)
    engine.set_enabled(game, two["id"], False)
    assert Path(game["path"], "original.txt").read_bytes() == b"one"
    engine.uninstall(game, one["id"])
    assert Path(game["path"], "original.txt").read_bytes() == b"vanilla"
    engine.set_enabled(game, two["id"], True)
    assert Path(game["path"], "original.txt").read_bytes() == b"two"


def test_new_files_removed_when_disabled_and_backups_private(tmp_path, game):
    engine = Deployment(tmp_path / "state")
    plan = prepare(engine, game, tmp_path, target="nested/new.pak")
    mod = engine.install(game, plan["id"])
    assert Path(game["path"], "nested/new.pak").is_file()
    engine.set_enabled(game, mod["id"], False)
    assert not Path(game["path"], "nested/new.pak").exists()
    assert (tmp_path / "state").stat().st_mode & 0o777 == 0o700


@pytest.mark.parametrize("action", ["disable", "uninstall", "install"])
def test_external_changes_are_never_overwritten(tmp_path, game, action):
    engine = Deployment(tmp_path / "state")
    mod = engine.install(game, prepare(engine, game, tmp_path)["id"], True)
    target = Path(game["path"], "original.txt")
    target.write_bytes(b"external update")
    with pytest.raises(ModsError, match="修改|冲突"):
        if action == "disable":
            engine.set_enabled(game, mod["id"], False)
        elif action == "uninstall":
            engine.uninstall(game, mod["id"])
        else:
            engine.install(game, prepare(engine, game, tmp_path, "two")["id"], True)
    assert target.read_bytes() == b"external update"


def test_target_symlink_and_game_build_change_reject_plan(tmp_path, game):
    engine = Deployment(tmp_path / "state")
    outside = tmp_path / "outside"
    outside.mkdir()
    Path(game["path"], "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ModsError):
        prepare(engine, game, tmp_path, target="linked/escape")
    plan = prepare(engine, game, tmp_path)
    with pytest.raises(ModsError, match="版本|变化|重新"):
        engine.install({**game, "build_id": "2"}, plan["id"], True)
    assert not (outside / "escape").exists()


def test_power_loss_journal_recovers_before_next_operation(tmp_path, game):
    def fault(index, target):
        raise KeyboardInterrupt("simulated power loss")

    engine = Deployment(tmp_path / "state", fault=fault)
    plan = prepare(engine, game, tmp_path)
    with pytest.raises(KeyboardInterrupt):
        engine.install(game, plan["id"], True)
    assert Path(game["path"], "original.txt").read_bytes() == b"mod"
    recovered = Deployment(tmp_path / "state")
    recovered.recover(game)
    assert Path(game["path"], "original.txt").read_bytes() == b"vanilla"
    assert recovered.list_mods(game["id"]) == []


def test_recovery_preserves_changes_made_after_crash(tmp_path, game):
    def fault(index, target):
        raise KeyboardInterrupt

    engine = Deployment(tmp_path / "state", fault=fault)
    with pytest.raises(KeyboardInterrupt):
        engine.install(game, prepare(engine, game, tmp_path)["id"], True)
    target = Path(game["path"], "original.txt")
    target.write_bytes(b"external")
    recovered = Deployment(tmp_path / "state")
    with pytest.raises(ModsError, match="恢复|修改|冲突"):
        recovered.recover(game)
    assert target.read_bytes() == b"external"


def test_blocked_layout_running_game_and_tampered_object_fail(tmp_path, game):
    engine = Deployment(tmp_path / "state")
    plan = engine.prepare(
        game,
        "unknown",
        tmp_path,
        {"files": [], "warnings": [], "requirements": [], "blocked_reason": "需要专用管理器"},
    )
    assert not plan["can_install"]
    with pytest.raises(ModsError):
        engine.install(game, plan["id"])
    with pytest.raises(ModsError, match="运行"):
        prepare(engine, {**game, "running": True}, tmp_path)


def test_re_paks_renumber_without_touching_official_patches(tmp_path, game):
    game = {**game, "pak_prefix": "re_chunk_000.pak.patch_", "pak_padding": 3}
    root = Path(game["path"])
    (root / "re_chunk_000.pak.patch_001.pak").write_bytes(b"official")
    engine = Deployment(tmp_path / "state")
    one = engine.install(
        game, prepare(engine, game, tmp_path, "one", b"one", "mod.pak", "re_pak")["id"]
    )
    two = engine.install(
        game, prepare(engine, game, tmp_path, "two", b"two", "mod.pak", "re_pak")["id"]
    )
    assert (root / "re_chunk_000.pak.patch_002.pak").read_bytes() == b"one"
    assert (root / "re_chunk_000.pak.patch_003.pak").read_bytes() == b"two"
    engine.set_enabled(game, one["id"], False)
    assert (root / "re_chunk_000.pak.patch_002.pak").read_bytes() == b"two"
    assert not (root / "re_chunk_000.pak.patch_003.pak").exists()
    engine.uninstall(game, two["id"])
    assert (root / "re_chunk_000.pak.patch_001.pak").read_bytes() == b"official"
    assert not (root / "re_chunk_000.pak.patch_002.pak").exists()
