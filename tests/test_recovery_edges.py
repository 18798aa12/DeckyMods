"""Observable deployment guarantees at real filesystem crash boundaries."""

import errno
import os
import stat

import decky_mods.gamefs as gamefs
import pytest
from decky_mods.deployment import Deployment
from decky_mods.errors import ModsError


@pytest.fixture
def installation(tmp_path):
    root = tmp_path / "Game"
    root.mkdir()
    originals = {"a.bin": b"vanilla-a", "b.bin": b"vanilla-b", "c.bin": b"vanilla-c"}
    for name, payload in originals.items():
        (root / name).write_bytes(payload)
    game = {"id": "crash-game", "path": str(root), "build_id": "1", "running": False}
    engine = Deployment(tmp_path / "state")
    return engine, game, root, originals


def make_plan(engine, game, tmp_path, targets=("a.bin",), name="test-mod"):
    extracted = tmp_path / name
    extracted.mkdir()
    files = []
    for index, target in enumerate(targets):
        source = f"payload-{index}.bin"
        (extracted / source).write_bytes(f"mod-{target}".encode())
        files.append({"source": source, "target": target})
    return engine.prepare(game, name, extracted, {"files": files})


def assert_originals(root, originals):
    assert {name: (root / name).read_bytes() for name in originals} == originals


@pytest.mark.parametrize("crash", [False, True], ids=["write-error", "power-loss"])
def test_incomplete_temporary_write_recovers_without_locking_game(
    installation, tmp_path, monkeypatch, crash
):
    engine, game, root, originals = installation
    plan = make_plan(engine, game, tmp_path)
    fsync = gamefs.os.fsync
    fired = False

    def interrupted_write(descriptor):
        nonlocal fired
        info = os.fstat(descriptor)
        is_deployment_temp = any(
            (path.stat().st_dev, path.stat().st_ino) == (info.st_dev, info.st_ino)
            for path in root.rglob(".deckymods-*")
        )
        if not fired and stat.S_ISREG(info.st_mode) and is_deployment_temp:
            fired = True
            os.ftruncate(descriptor, 3)
            if crash:
                raise KeyboardInterrupt("power lost during temporary write")
            raise OSError(errno.ENOSPC, "disk filled during temporary write")
        return fsync(descriptor)

    with monkeypatch.context() as patch:
        patch.setattr(gamefs.os, "fsync", interrupted_write)
        with pytest.raises(KeyboardInterrupt if crash else ModsError):
            engine.install(game, plan["id"], True)
    assert fired
    assert_originals(root, originals)

    restarted = Deployment(tmp_path / "state")
    restarted.recover(game)
    assert restarted.db.pending(game["id"]) == []
    assert list(root.rglob(".deckymods-*")) == []
    installed = restarted.install(game, plan["id"], True)
    assert (root / "a.bin").read_bytes() == b"mod-a.bin"
    restarted.uninstall(game, installed["id"])
    assert_originals(root, originals)


def test_crash_immediately_after_exchange_restores_displaced_original(
    installation, tmp_path, monkeypatch
):
    engine, game, root, originals = installation
    plan = make_plan(engine, game, tmp_path)
    rename = gamefs.rename_at

    def exchange_then_crash(parent, source, target, *, exchange):
        rename(parent, source, target, exchange=exchange)
        if exchange:
            raise KeyboardInterrupt("crash after atomic exchange before old-file unlink")

    with monkeypatch.context() as patch:
        patch.setattr(gamefs, "rename_at", exchange_then_crash)
        with pytest.raises(KeyboardInterrupt):
            engine.install(game, plan["id"], True)
    assert (root / "a.bin").read_bytes() == b"mod-a.bin"
    assert [path.read_bytes() for path in root.glob(".deckymods-*")] == [b"vanilla-a"]
    restarted = Deployment(tmp_path / "state")
    restarted.recover(game)
    assert_originals(root, originals)
    assert list(root.rglob(".deckymods-*")) == []
    assert restarted.list_mods(game["id"]) == []
    assert restarted.db.pending(game["id"]) == []


def test_multi_file_crash_restores_changed_and_untouched_files(installation, tmp_path):
    engine, game, root, originals = installation
    plan = make_plan(engine, game, tmp_path, tuple(originals))

    def crash_midway(index, target):
        if index == 1:
            raise KeyboardInterrupt("second of three files completed")

    engine.fault = crash_midway
    with pytest.raises(KeyboardInterrupt):
        engine.install(game, plan["id"], True)
    assert (root / "a.bin").read_bytes() == b"mod-a.bin"
    assert (root / "b.bin").read_bytes() == b"mod-b.bin"
    assert (root / "c.bin").read_bytes() == originals["c.bin"]

    restarted = Deployment(tmp_path / "state")
    restarted.recover(game)
    assert_originals(root, originals)
    assert restarted.list_mods(game["id"]) == []
    assert restarted.db.pending(game["id"]) == []
    assert list(root.rglob(".deckymods-*")) == []


def test_crash_during_new_file_removal_restores_installed_mod(installation, tmp_path, monkeypatch):
    engine, game, root, _ = installation
    plan = make_plan(engine, game, tmp_path, ("added.bin",))
    mod = engine.install(game, plan["id"])
    rename = gamefs.rename_at

    def remove_then_crash(parent, source, target, *, exchange):
        rename(parent, source, target, exchange=exchange)
        if not exchange and source == "added.bin":
            raise KeyboardInterrupt("crash after removal rename before unlink")

    with monkeypatch.context() as patch:
        patch.setattr(gamefs, "rename_at", remove_then_crash)
        with pytest.raises(KeyboardInterrupt):
            engine.set_enabled(game, mod["id"], False)
    assert not (root / "added.bin").exists()
    restarted = Deployment(tmp_path / "state")
    restarted.recover(game)
    assert (root / "added.bin").read_bytes() == b"mod-added.bin"
    assert restarted.list_mods(game["id"])[0]["enabled"]
    assert restarted.db.pending(game["id"]) == []
    assert list(root.rglob(".deckymods-*")) == []
    restarted.set_enabled(game, mod["id"], False)
    assert not (root / "added.bin").exists()


def test_temporary_unlink_failure_rolls_back_and_allows_retry(installation, tmp_path, monkeypatch):
    engine, game, root, originals = installation
    plan = make_plan(engine, game, tmp_path)
    unlink = gamefs.os.unlink
    fired = False

    def fail_old_file_unlink(path, *args, **kwargs):
        nonlocal fired
        if not fired and str(path).startswith(".deckymods-"):
            fired = True
            raise OSError(errno.EPERM, "temporary removal denied")
        return unlink(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(gamefs.os, "unlink", fail_old_file_unlink)
        with pytest.raises(ModsError, match="失败|恢复"):
            engine.install(game, plan["id"], True)
    assert fired
    assert_originals(root, originals)
    assert engine.db.pending(game["id"]) == []
    assert list(root.rglob(".deckymods-*")) == []
    engine.install(game, plan["id"], True)
    assert (root / "a.bin").read_bytes() == b"mod-a.bin"


def test_recovery_can_resume_after_its_own_temporary_write_is_interrupted(
    installation, tmp_path, monkeypatch
):
    engine, game, root, originals = installation
    plan = make_plan(engine, game, tmp_path)

    def initial_crash(index, target):
        raise KeyboardInterrupt("initial deployment crashed")

    engine.fault = initial_crash
    with pytest.raises(KeyboardInterrupt):
        engine.install(game, plan["id"], True)
    restarted = Deployment(tmp_path / "state")
    fsync = gamefs.os.fsync
    fired = False

    def crash_recovery_write(descriptor):
        nonlocal fired
        info = os.fstat(descriptor)
        is_rollback_temp = any(
            (path.stat().st_dev, path.stat().st_ino) == (info.st_dev, info.st_ino)
            for path in root.rglob(".deckymods-*_r")
        )
        if not fired and stat.S_ISREG(info.st_mode) and is_rollback_temp:
            fired = True
            os.ftruncate(descriptor, 3)
            raise KeyboardInterrupt("power lost during recovery temporary write")
        return fsync(descriptor)

    with monkeypatch.context() as patch:
        patch.setattr(gamefs.os, "fsync", crash_recovery_write)
        with pytest.raises(KeyboardInterrupt):
            restarted.recover(game)
    assert fired
    assert (root / "a.bin").read_bytes() == b"mod-a.bin"
    final_restart = Deployment(tmp_path / "state")
    final_restart.recover(game)
    assert_originals(root, originals)
    assert final_restart.db.pending(game["id"]) == []
    assert list(root.rglob(".deckymods-*")) == []


def test_recovery_preserves_external_file_displaced_by_interrupted_rollback(
    installation, tmp_path, monkeypatch
):
    engine, game, root, _ = installation
    plan = make_plan(engine, game, tmp_path)

    def initial_crash(index, target):
        raise KeyboardInterrupt("initial deployment crashed")

    engine.fault = initial_crash
    with pytest.raises(KeyboardInterrupt):
        engine.install(game, plan["id"], True)
    rename = gamefs.rename_at

    def race_rollback_then_crash(parent, source, target, *, exchange):
        if exchange and source.endswith("_r"):
            descriptor = os.open(target, os.O_WRONLY | os.O_TRUNC, dir_fd=parent)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(b"external while restoring original")
        rename(parent, source, target, exchange=exchange)
        if exchange and source.endswith("_r"):
            raise KeyboardInterrupt("crash before checking displaced rollback file")

    restarted = Deployment(tmp_path / "state")
    with monkeypatch.context() as patch:
        patch.setattr(gamefs, "rename_at", race_rollback_then_crash)
        with pytest.raises(KeyboardInterrupt):
            restarted.recover(game)
    before_recovery = {path.name: path.read_bytes() for path in root.iterdir()}
    assert b"external while restoring original" in before_recovery.values()
    final_restart = Deployment(tmp_path / "state")
    with pytest.raises(ModsError, match="恢复|修改|保留"):
        final_restart.recover(game)
    assert {path.name: path.read_bytes() for path in root.iterdir()} == before_recovery
    assert final_restart.db.pending(game["id"])


def test_recovery_validates_displaced_external_bytes_before_changing_target(
    installation, tmp_path, monkeypatch
):
    engine, game, root, _ = installation
    plan = make_plan(engine, game, tmp_path)
    rename = gamefs.rename_at

    def external_change_then_crash(parent, source, target, *, exchange):
        if exchange:
            descriptor = os.open(target, os.O_WRONLY | os.O_TRUNC, dir_fd=parent)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(b"external save after checksum")
        rename(parent, source, target, exchange=exchange)
        if exchange:
            raise KeyboardInterrupt("crash before displaced-file validation")

    with monkeypatch.context() as patch:
        patch.setattr(gamefs, "rename_at", external_change_then_crash)
        with pytest.raises(KeyboardInterrupt):
            engine.install(game, plan["id"], True)
    before_recovery = {path.name: path.read_bytes() for path in root.iterdir()}
    assert b"external save after checksum" in before_recovery.values()

    restarted = Deployment(tmp_path / "state")
    with pytest.raises(ModsError, match="恢复|修改|保留"):
        restarted.recover(game)
    assert {path.name: path.read_bytes() for path in root.iterdir()} == before_recovery
    assert restarted.db.pending(game["id"])


def test_metadata_commit_failure_restores_files_and_keeps_plan_retryable(
    installation, tmp_path, monkeypatch
):
    engine, game, root, originals = installation
    plan = make_plan(engine, game, tmp_path, tuple(originals))
    finish = engine.db.finish

    def fail_metadata_commit(operation, state, *, committed):
        if committed:
            raise OSError(errno.ENOSPC, "database commit failed")
        return finish(operation, state, committed=committed)

    with monkeypatch.context() as patch:
        patch.setattr(engine.db, "finish", fail_metadata_commit)
        with pytest.raises(ModsError, match="失败|恢复"):
            engine.install(game, plan["id"], True)
    assert_originals(root, originals)
    assert engine.list_mods(game["id"]) == []
    assert engine.db.pending(game["id"]) == []
    assert engine.get_plan(plan["id"])["can_install"]
    assert list(root.rglob(".deckymods-*")) == []
    engine.install(game, plan["id"], True)
    assert (root / "c.bin").read_bytes() == b"mod-c.bin"


def test_corrupt_object_is_rejected_before_any_game_file_changes(installation, tmp_path):
    engine, game, root, originals = installation
    plan = make_plan(engine, game, tmp_path, tuple(originals))
    stored_plan = engine.db.plan(plan["id"])
    corrupt = engine.objects.path(stored_plan["mod"]["files"][1]["hash"])
    corrupt.chmod(0o600)
    corrupt.write_bytes(b"corrupted cache")
    with pytest.raises(ModsError, match="校验|对象|备份"):
        engine.install(game, plan["id"], True)
    assert_originals(root, originals)
    assert engine.db.pending(game["id"]) == []
    assert engine.list_mods(game["id"]) == []
    assert list(root.rglob(".deckymods-*")) == []


def test_corrupt_baseline_does_not_remove_the_working_mod(installation, tmp_path):
    engine, game, root, _ = installation
    plan = make_plan(engine, game, tmp_path)
    mod = engine.install(game, plan["id"], True)
    baseline = engine.db.game(game["id"])["baseline"]["a.bin"]
    backup = engine.objects.path(baseline)
    backup.chmod(0o600)
    backup.write_bytes(b"corrupt original backup")
    with pytest.raises(ModsError, match="校验|对象|备份"):
        engine.uninstall(game, mod["id"])
    assert (root / "a.bin").read_bytes() == b"mod-a.bin"
    assert engine.list_mods(game["id"])[0]["enabled"]
    assert engine.db.pending(game["id"]) == []


def test_casefold_collision_across_mods_is_not_deployed(installation, tmp_path):
    engine, game, root, _ = installation
    first_plan = make_plan(engine, game, tmp_path, ("Textures/Hero.pak",), "first")
    first = engine.install(game, first_plan["id"])
    try:
        second_plan = make_plan(engine, game, tmp_path, ("textures/hero.pak",), "second")
    except ModsError as error:
        assert "大小写" in str(error) or "冲突" in str(error)
    else:
        assert not second_plan["can_install"]
        with pytest.raises(ModsError):
            engine.install(game, second_plan["id"], True)
    assert (root / "Textures/Hero.pak").read_bytes() == b"mod-Textures/Hero.pak"
    deployed_names = {path.relative_to(root).as_posix() for path in root.rglob("*")}
    assert "textures/hero.pak" not in deployed_names
    assert [mod["id"] for mod in engine.list_mods(game["id"])] == [first["id"]]
