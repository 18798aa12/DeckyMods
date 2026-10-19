"""Known launch requirements merge without losing user settings or backup history."""

import json
import stat

import pytest
from decky_mods.errors import ModsError
from decky_mods.launch_options import LaunchOptions


@pytest.fixture
def setup(tmp_path):
    root = tmp_path / "RE7"
    root.mkdir()
    (root / "dinput8.dll").write_bytes(b"loader")
    game = {
        "id": "resident_evil_7",
        "adapter": "reframework",
        "installed": True,
        "running": False,
        "updating": False,
        "path": str(root),
        "app_id": "418370",
    }
    return LaunchOptions(tmp_path / "private"), game


def complete(manager, game, current):
    change = manager.prepare(game, current)
    if change["changed"]:
        manager.finish(game, change["id"], change["after"])
    return change


def test_detection_requires_reviewed_adapter_and_regular_loader(setup, tmp_path):
    manager, game = setup
    assert manager.status(game) == {
        "supported": True,
        "required": True,
        "reason": "检测到 REFramework，需要 Proton DLL 启动项；将保留已有插帧与其他参数。",
        "app_id": "418370",
        "auto_enabled": True,
        "backup_available": False,
    }
    assert not manager.status({**game, "adapter": "ue_pak"})["supported"]
    loader = tmp_path / "RE7/dinput8.dll"
    loader.unlink()
    assert not manager.status(game)["required"]
    target = tmp_path / "outside.dll"
    target.write_bytes(b"loader")
    loader.symlink_to(target)
    assert not manager.status(game)["required"]


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("", 'WINEDLLOVERRIDES="dinput8.dll=n,b" %command%'),
        ("  ", 'WINEDLLOVERRIDES="dinput8.dll=n,b" %command%  '),
        ("%command%", 'WINEDLLOVERRIDES="dinput8.dll=n,b" %command%'),
        (
            'FOO="a b"  WINEDLLOVERRIDES="dxgi=n,b" %command% -windowed',
            'FOO="a b"  WINEDLLOVERRIDES="dxgi=n,b;dinput8.dll=n,b" %command% -windowed',
        ),
        (
            "WINEDLLOVERRIDES='dxgi=n,b' %command%",
            "WINEDLLOVERRIDES='dxgi=n,b;dinput8.dll=n,b' %command%",
        ),
        (
            "WINEDLLOVERRIDES=dxgi=n,b %command%",
            'WINEDLLOVERRIDES="dxgi=n,b;dinput8.dll=n,b" %command%',
        ),
        (
            'WINEDLLOVERRIDES="" %command%',
            'WINEDLLOVERRIDES="dinput8.dll=n,b" %command%',
        ),
        (
            "env FOO=bar mangohud gamemoderun %command% --title 'Game Name'",
            'env FOO=bar WINEDLLOVERRIDES="dinput8.dll=n,b" '
            "mangohud gamemoderun %command% --title 'Game Name'",
        ),
    ],
)
def test_merge_preserves_original_options(setup, before, after):
    manager, game = setup
    change = manager.prepare(game, before)
    assert change["before"] == before
    assert change["after"] == after
    assert change["changed"]
    assert change["app_id"] == game["app_id"]
    assert manager.status(game)["backup_available"]
    assert manager.finish(game, change["id"], after)["required"]
    assert not manager.prepare(game, after)["changed"]


@pytest.mark.parametrize("entry", ["dinput8=n,b", "dinput8.dll=n,b", "dinput8=native,builtin"])
def test_existing_compatible_alias_is_idempotent(setup, entry):
    manager, game = setup
    current = f'WINEDLLOVERRIDES="dxgi=n,b;{entry}" %command%'
    change = manager.prepare(game, current)
    assert not change["changed"]
    assert change["after"] == current
    assert not manager.status(game)["backup_available"]


@pytest.mark.parametrize(
    "current",
    [
        "-windowed",
        'WINEDLLOVERRIDES="dinput8=b" %command%',
        'WINEDLLOVERRIDES="dinput8=n,b;dinput8.dll=n,b" %command%',
        'WINEDLLOVERRIDES="dxgi=n,b;dxgi=b" %command%',
        'WINEDLLOVERRIDES="dxgi=n,b;" %command%',
        'WINEDLLOVERRIDES="dxgi=n,b" WINEDLLOVERRIDES="dxgi=n,b" %command%',
        'WINEDLLOVERRIDES="$SECRET" %command%',
        'WINEDLLOVERRIDES="dxgi=n,b" %command%; rm SECRET',
        "echo SECRET && %command%",
        'sh -c "%command% SECRET"',
        "%command% `SECRET`",
        "%command% $(SECRET)",
        "%command%\nSECRET",
        'WINEDLLOVERRIDES="dxgi=n,b %command%',
        "%command% %command%",
        "%command% --arg=%command%",
        '"%command%"',
        "WINEDLLOVERRIDES='dxgi=n,b'garbage %command%",
        "%command% WINEDLLOVERRIDES=dxgi=n,b",
        "%command% [ab]",
    ],
)
def test_ambiguous_options_fail_closed_without_leaking_text(setup, current):
    manager, game = setup
    with pytest.raises(ModsError) as error:
        manager.prepare(game, current)
    assert "SECRET" not in str(error.value)
    assert not manager.status(game)["backup_available"]


@pytest.mark.parametrize("flag", ["running", "updating"])
def test_writes_blocked_for_busy_game(setup, flag):
    manager, game = setup
    busy = {**game, flag: True}
    with pytest.raises(ModsError):
        manager.prepare(busy, "")
    with pytest.raises(ModsError):
        manager.set_auto(busy, False)


def test_settings_persist_without_loader_and_disabled_auto_never_merges(setup):
    manager, game = setup
    (manager.directory.parent / "RE7/dinput8.dll").unlink()
    assert not manager.set_auto(game, False)["auto_enabled"]
    manager2 = LaunchOptions(manager.directory)
    assert not manager2.status(game)["auto_enabled"]
    manager2.set_auto(game, True)
    with pytest.raises(ModsError):
        manager2.prepare(game, "")


def test_disabled_auto_requires_explicit_enable(setup):
    manager, game = setup
    manager.set_auto(game, False)
    with pytest.raises(ModsError):
        manager.prepare(game, "")


def test_disabling_auto_prevents_retry_of_a_prepared_write(setup):
    manager, game = setup
    change = manager.prepare(game, "%command%")
    manager.set_auto(game, False)
    with pytest.raises(ModsError):
        manager.prepare(game, "%command%")
    # A Steam write already in flight may still be acknowledged without re-enabling auto.
    assert not manager.finish(game, change["id"], change["after"])["auto_enabled"]


def test_pending_reconciles_success_after_backend_restart(setup):
    manager, game = setup
    change = manager.prepare(game, "%command%")
    restarted = LaunchOptions(manager.directory)
    assert not restarted.prepare(game, change["after"])["changed"]
    restored = restarted.prepare(game, change["after"], restore=True)
    assert restored["after"] == "%command%"
    restarted.finish(game, restored["id"], restored["after"])
    assert not restarted.status(game)["auto_enabled"]


def test_pending_retries_when_steam_was_never_written(setup):
    manager, game = setup
    change = manager.prepare(game, "%command%")
    retry = manager.prepare(game, "%command%")
    assert retry == change


def test_pending_external_edits_and_wrong_finish_are_blocked(setup):
    manager, game = setup
    change = manager.prepare(game, "%command%")
    with pytest.raises(ModsError):
        manager.finish(game, "wrong-id", change["after"])
    with pytest.raises(ModsError):
        manager.finish(game, change["id"], "%command% -SECRET")
    with pytest.raises(ModsError):
        manager.prepare(game, "%command% -SECRET")


def test_restore_keeps_original_immutable_and_rejects_later_user_edits(setup):
    manager, game = setup
    original = 'WINEDLLOVERRIDES="dxgi=n,b" %command%'
    change = complete(manager, game, original)
    edited = change["after"] + " -windowed"
    with pytest.raises(ModsError):
        manager.prepare(game, edited, restore=True)
    # Ordinary auto checks leave a compatible user's extra arguments untouched.
    assert not manager.prepare(game, edited)["changed"]
    with pytest.raises(ModsError):
        manager.prepare(game, edited, restore=True)
    with pytest.raises(ModsError, match="外部更改"):
        manager.prepare(game, change["after"], restore=True)


def test_auto_remerge_preserves_later_additions_and_original_backup(setup):
    manager, game = setup
    complete(manager, game, "%command%")
    change = complete(manager, game, "FOO=bar %command% -windowed")
    assert change["after"] == 'FOO=bar WINEDLLOVERRIDES="dinput8.dll=n,b" %command% -windowed'
    with pytest.raises(ModsError, match="外部更改"):
        manager.prepare(game, change["after"], restore=True)
    saved = json.loads((manager.directory / "418370.json").read_text())
    assert saved["original"] == "%command%"


def test_external_compliant_edit_permanently_disables_snapshot_restore(setup):
    manager, game = setup
    change = complete(manager, game, "%command%")
    edited = change["after"] + " -windowed"
    assert not manager.prepare(game, edited)["changed"]
    with pytest.raises(ModsError, match="外部更改"):
        manager.prepare(game, edited, restore=True)
    manager.set_auto(game, False)
    manager.set_auto(game, True)
    # Returning to an earlier known command cannot reset the monotonic safety flag.
    with pytest.raises(ModsError, match="外部更改"):
        manager.prepare(game, change["after"], restore=True)


def test_interrupted_remerge_reconciliation_marks_external_edit_unsafe(setup):
    manager, game = setup
    first = complete(manager, game, "%command%")
    change = manager.prepare(game, "%command% -windowed")
    path = manager.directory / "418370.json"
    saved = json.loads(path.read_text())
    assert saved["last_written"] == first["after"]
    # Simulate a previous writer interrupted before the safety flag was recorded.
    path.write_text(json.dumps({**saved, "restore_safe": True}))
    restarted = LaunchOptions(manager.directory)
    assert not restarted.prepare(game, change["after"])["changed"]
    with pytest.raises(ModsError, match="外部更改"):
        restarted.prepare(game, change["after"], restore=True)


def test_backup_only_interruption_then_external_edit_disables_restore(setup):
    manager, game = setup
    manager.prepare(game, "%command%")
    path = manager.directory / "418370.json"
    saved = json.loads(path.read_text())
    # The first backup fsync succeeded but the intent journal was never written.
    path.write_text(json.dumps({**saved, "pending": None}))
    restarted = LaunchOptions(manager.directory)
    change = complete(restarted, game, "%command% -windowed")
    with pytest.raises(ModsError, match="外部更改"):
        restarted.prepare(game, change["after"], restore=True)
    assert json.loads(path.read_text())["original"] == "%command%"


def test_external_change_seen_during_finish_permanently_blocks_restore(setup):
    manager, game = setup
    change = manager.prepare(game, "%command%")
    with pytest.raises(ModsError):
        manager.finish(game, change["id"], change["after"] + " -windowed")
    manager.finish(game, change["id"], change["after"])
    with pytest.raises(ModsError, match="外部更改"):
        manager.prepare(game, change["after"], restore=True)


def test_restore_works_if_loader_removed_but_still_checks_busy_state(setup):
    manager, game = setup
    change = complete(manager, game, "")
    (manager.directory.parent / "RE7/dinput8.dll").unlink()
    with pytest.raises(ModsError):
        manager.prepare({**game, "running": True}, change["after"], restore=True)
    restore = manager.prepare(game, change["after"], restore=True)
    assert restore["after"] == ""


def test_private_journal_permissions_and_no_secret_in_error(setup):
    manager, game = setup
    manager.prepare(game, "TOKEN=PRIVATE_VALUE %command%")
    assert stat.S_IMODE(manager.directory.stat().st_mode) == 0o700
    path = manager.directory / "418370.json"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    saved = json.loads(path.read_text())
    assert saved["original"] == "TOKEN=PRIVATE_VALUE %command%"
    path.write_text("{broken PRIVATE_VALUE")
    with pytest.raises(ModsError) as error:
        manager.status(game)
    assert "PRIVATE_VALUE" not in str(error.value)


def test_symlinked_private_file_and_root_are_rejected(setup, tmp_path):
    manager, game = setup
    manager.set_auto(game, False)
    file = manager.directory / "418370.json"
    file.unlink()
    outside = tmp_path / "other.json"
    outside.write_text("{}")
    file.symlink_to(outside)
    with pytest.raises(ModsError):
        manager.status(game)
    assert outside.read_text() == "{}"
    linked = tmp_path / "linked-game"
    linked.symlink_to(tmp_path / "RE7", target_is_directory=True)
    assert not manager.status({**game, "path": str(linked)})["supported"]


def test_invalid_game_or_input_never_writes(setup):
    manager, game = setup
    for bad in (
        {**game, "installed": False},
        {**game, "adapter": "catalog_only"},
        {**game, "app_id": "../bad"},
        {**game, "app_id": "4294967296"},
    ):
        with pytest.raises(ModsError):
            manager.prepare(bad, "")
    with pytest.raises(ModsError):
        manager.prepare(game, "x" * 32769)
    with pytest.raises(ModsError):
        manager.prepare(game, "中" * 6000)
    with pytest.raises(ModsError):
        manager.prepare(game, "\ud800")
    with pytest.raises(ModsError):
        manager.set_auto(game, "yes")
    assert not list(manager.directory.glob("*.json"))


def test_private_directory_and_game_ancestors_cannot_be_symlinks(setup, tmp_path):
    manager, game = setup
    linked = tmp_path / "alias"
    linked.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ModsError):
        LaunchOptions(linked / "new-state")
    assert not (tmp_path / "new-state").exists()
    assert not manager.status({**game, "path": str(linked / "RE7")})["supported"]
