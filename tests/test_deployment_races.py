"""Never accept a fresh filesystem hash as consent to overwrite a concurrent edit."""

import pytest
from decky_mods.deployment import Deployment
from decky_mods.errors import ModsError
from decky_mods.gamefs import GameFiles


@pytest.fixture
def deployment(tmp_path):
    directory = tmp_path / "Game"
    directory.mkdir()
    (directory / "original.bin").write_bytes(b"vanilla")
    game = {"id": "race-game", "path": str(directory), "build_id": "1", "running": False}
    return Deployment(tmp_path / "state"), game, directory / "original.bin"


def plan(engine, game, tmp_path, name, payload):
    extracted = tmp_path / name
    extracted.mkdir()
    (extracted / "mod.bin").write_bytes(payload)
    return engine.prepare(
        game,
        name,
        extracted,
        {"files": [{"source": "mod.bin", "target": "original.bin"}]},
    )


def test_change_after_initial_baseline_capture_is_not_implicit_overwrite_consent(
    deployment, tmp_path, monkeypatch
):
    engine, game, target = deployment
    prepared = plan(engine, game, tmp_path, "first", b"mod")
    capture = GameFiles.capture
    injected = False

    def capture_then_external_change(files, relative):
        nonlocal injected
        result = capture(files, relative)
        if relative == "original.bin" and not injected:
            injected = True
            target.write_bytes(b"external after baseline capture")
        return result

    monkeypatch.setattr(GameFiles, "capture", capture_then_external_change)
    with pytest.raises(ModsError, match="修改|冲突|恢复|失败"):
        engine.install(game, prepared["id"], allow_conflicts=True)
    assert injected
    assert target.read_bytes() == b"external after baseline capture"
    assert engine.list_mods(game["id"]) == []


@pytest.mark.parametrize("action", ["install", "disable", "uninstall"])
def test_change_after_managed_file_check_is_not_retrusted(
    deployment, tmp_path, monkeypatch, action
):
    engine, game, target = deployment
    first_plan = plan(engine, game, tmp_path, "first", b"first mod")
    installed = engine.install(game, first_plan["id"], allow_conflicts=True)
    second_plan = plan(engine, game, tmp_path, "second", b"second mod")
    file_hash = GameFiles.hash
    injected = False

    def hash_then_external_change(files, relative):
        nonlocal injected
        result = file_hash(files, relative)
        if relative == "original.bin" and not injected:
            injected = True
            target.write_bytes(b"external after managed-file check")
        return result

    monkeypatch.setattr(GameFiles, "hash", hash_then_external_change)
    with pytest.raises(ModsError, match="修改|冲突|恢复|失败"):
        if action == "install":
            engine.install(game, second_plan["id"], allow_conflicts=True)
        elif action == "disable":
            engine.set_enabled(game, installed["id"], False)
        else:
            engine.uninstall(game, installed["id"])
    assert injected
    assert target.read_bytes() == b"external after managed-file check"
    records = engine.list_mods(game["id"])
    assert [mod["id"] for mod in records] == [installed["id"]]
    assert records[0]["enabled"]
