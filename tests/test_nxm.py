import subprocess
import sys
from pathlib import Path

import pytest
from decky_mods.errors import ModsError
from decky_mods.nxm import NxmHandler
from decky_mods.nxm_helper import enqueue


@pytest.fixture
def handler(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr("decky_mods.nxm.sys.platform", "linux")
    monkeypatch.setattr("decky_mods.nxm.shutil.which", lambda _name: "/usr/bin/xdg-mime")
    state = {"default": "old-manager.desktop", "calls": []}

    def run(argv, **kwargs):
        state["calls"].append(argv)
        if "query" in argv:
            return subprocess.CompletedProcess(argv, 0, state["default"] + "\n", "")
        state["default"] = argv[2]
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr("decky_mods.nxm.subprocess.run", run)
    return NxmHandler(home / ".local/share/DeckyMods", Path(__file__).parents[1], home), state


def test_foreign_xdg_config_remains_blocked(handler, monkeypatch, tmp_path):
    nxm, _ = handler
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "foreign"))
    with pytest.raises(ModsError, match="当前用户"):
        nxm._remove_empty_default(nxm.home / ".local/share/applications")


def test_handler_opt_in_preserves_restores_previous(handler):
    nxm, state = handler
    assert not nxm.status()["enabled"]
    assert nxm.set_enabled(True)["previous"] == "old-manager.desktop"
    desktop = nxm.home / ".local/share/applications/decky-mods-nxm.desktop"
    contents = desktop.read_text()
    assert "nxm_helper.py" in contents
    # Freedesktop explicitly leaves field-code expansion in quotes undefined.
    assert next(line for line in contents.splitlines() if line.startswith("Exec=")).endswith(" %u")
    assert "Terminal=false" in contents
    assert nxm.set_enabled(False)["enabled"] is False
    assert state["default"] == "old-manager.desktop"
    assert not desktop.exists()


def test_never_overwrites_new_external_association(handler):
    nxm, state = handler
    nxm.set_enabled(True)
    state["default"] = "new-manager.desktop"
    nxm.set_enabled(False)
    assert state["default"] == "new-manager.desktop"


def test_private_queue_handoff_when_plugin_stopped_and_drain(handler):
    nxm, _ = handler
    uri = "nxm://stellarblade/mods/5/files/10?key=secret&expires=9999999999&user_id=42"
    queue = nxm.directory / "inbox"
    enqueue(queue, uri)
    files = list(queue.iterdir())
    assert len(files) == 1 and files[0].stat().st_mode & 0o777 == 0o600
    assert queue.stat().st_mode & 0o777 == 0o700
    assert nxm.drain() == [uri]
    assert nxm.drain() == []
    assert list(queue.iterdir()) == []


def test_queue_refuses_symlinks_and_oversize(handler, tmp_path):
    nxm, _ = handler
    queue = nxm.directory / "inbox"
    victim = tmp_path / "victim"
    victim.write_text("private")
    (queue / "a.json").symlink_to(victim)
    assert nxm.drain() == []
    assert victim.read_text() == "private"
    with pytest.raises((ModsError, ValueError)):
        enqueue(queue, "nxm://" + "x" * 9000)


def test_helper_runs_standalone_and_never_echoes_token(tmp_path):
    helper = Path(__file__).parents[1] / "py_modules/decky_mods/nxm_helper.py"
    queue = tmp_path / "queue"
    result = subprocess.run(
        [
            sys.executable,
            str(helper),
            "--queue",
            str(queue),
            "nxm://stellarblade/mods/5/files/10?key=secret",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == "" and "secret" not in result.stderr
    assert len(list(queue.iterdir())) == 1


def test_handler_unsupported_platform_never_registers(tmp_path, monkeypatch):
    monkeypatch.setattr("decky_mods.nxm.sys.platform", "darwin")
    nxm = NxmHandler(tmp_path / "state", tmp_path, tmp_path)
    assert not nxm.status()["supported"]
    with pytest.raises(ModsError):
        nxm.set_enabled(True)


def test_duplicate_enable_keeps_original_previous(handler):
    nxm, _ = handler
    nxm.set_enabled(True)
    nxm.set_enabled(True)
    assert nxm.status()["previous"] == "old-manager.desktop"


def test_refuses_foreign_desktop_file(handler):
    nxm, _ = handler
    desktop = nxm.home / ".local/share/applications/decky-mods-nxm.desktop"
    desktop.parent.mkdir(parents=True)
    desktop.write_text("another program")
    with pytest.raises(ModsError):
        nxm.set_enabled(True)


def test_enqueue_publishes_only_complete_json(handler, monkeypatch):
    import decky_mods.nxm_helper as helper

    nxm, _ = handler
    original = helper.json.dump

    def dump(value, output):
        assert nxm.drain() == []
        original(value, output)

    monkeypatch.setattr(helper.json, "dump", dump)
    uri = "nxm://stellarblade/mods/5/files/10?key=secret"
    enqueue(nxm.directory / "inbox", uri)
    assert nxm.drain() == [uri]


def test_consumer_can_drain_immediately_after_publication(handler, monkeypatch):
    import decky_mods.nxm_helper as helper

    nxm, _ = handler
    handed_off = []
    original_link, original_rename = helper.os.link, helper.os.rename

    def after_link(source, target):
        original_link(source, target)
        handed_off.extend(nxm.drain())

    def after_rename(source, target):
        original_rename(source, target)
        handed_off.extend(nxm.drain())

    monkeypatch.setattr(helper.os, "link", after_link)
    monkeypatch.setattr(helper.os, "rename", after_rename)
    uri = "nxm://stellarblade/mods/5/files/10?key=publication-test"
    enqueue(nxm.directory / "inbox", uri)
    assert handed_off == [uri]
    assert nxm.drain() == []


def test_queue_uuid_collision_does_not_replace_existing_entry(handler, monkeypatch):
    import decky_mods.nxm_helper as helper

    nxm, _ = handler
    queue = nxm.directory / "inbox"
    unique = helper.uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    monkeypatch.setattr(helper.uuid, "uuid4", lambda: unique)
    first = "nxm://stellarblade/mods/5/files/10?key=first"
    enqueue(queue, first)
    with pytest.raises((FileExistsError, ValueError)):
        enqueue(queue, "nxm://stellarblade/mods/5/files/10?key=second")
    assert nxm.drain() == [first]


def test_unset_without_previous_removes_only_own_association(handler):
    nxm, _ = handler
    config = nxm.home / ".config/mimeapps.list"
    config.parent.mkdir()
    config.write_text(
        "[Default Applications]\nx-scheme-handler/nxm=decky-mods-nxm.desktop;\n"
        "text/plain=editor.desktop;\n[Added Associations]\n"
        "x-scheme-handler/nxm=decky-mods-nxm.desktop;other.desktop;\n"
    )
    nxm._remove_empty_default(nxm.home / ".local/share/applications")
    saved = config.read_text()
    assert "decky-mods-nxm.desktop" not in saved
    assert "editor.desktop" in saved and "other.desktop" in saved


def test_unset_without_previous_rejects_symlink(handler, tmp_path):
    nxm, _ = handler
    config = nxm.home / ".config/mimeapps.list"
    config.parent.mkdir()
    victim = tmp_path / "victim-mime"
    victim.write_text("do not change")
    config.symlink_to(victim)
    with pytest.raises(ModsError):
        nxm._remove_empty_default(nxm.home / ".local/share/applications")
    assert victim.read_text() == "do not change"


def test_queue_discards_stale_invalid_and_symlink_entries(handler, tmp_path):
    import json

    nxm, _ = handler
    queue = nxm.directory / "inbox"
    (queue / ("a" * 32 + ".json")).write_text("invalid")
    (queue / ("b" * 32 + ".json")).write_text(
        json.dumps({"created": 0, "uri": "nxm://stellarblade/mods/5/files/10?key=expired"})
    )
    victim = tmp_path / "signed"
    victim.write_text("must remain")
    (queue / ("c" * 32 + ".json")).symlink_to(victim)
    assert nxm.drain() == []
    assert list(queue.iterdir()) == []
    assert victim.read_text() == "must remain"


def test_status_reports_query_failure_safely(handler, monkeypatch):
    nxm, _ = handler

    def run(*args, **kwargs):
        raise subprocess.TimeoutExpired("xdg-mime", 10)

    monkeypatch.setattr("decky_mods.nxm.subprocess.run", run)
    status = nxm.status()
    assert not status["enabled"] and "xdg-mime" in status["message"]


def test_queue_bound_and_stale_cleanup(handler, monkeypatch):
    import os

    import decky_mods.nxm_helper as helper

    nxm, _ = handler
    queue = nxm.directory / "inbox"
    old = queue / ("a" * 32 + ".json")
    old.write_text("expired")
    os.utime(old, (1, 1))
    enqueue(queue, "nxm://stellarblade/mods/5/files/10?key=one")
    assert not old.exists()
    monkeypatch.setattr(helper, "MAX_QUEUE", 1)
    with pytest.raises(ValueError, match="full"):
        enqueue(queue, "nxm://stellarblade/mods/5/files/10?key=two")


def test_helper_cli_error_does_not_expose_input(tmp_path):
    helper = Path(__file__).parents[1] / "py_modules/decky_mods/nxm_helper.py"
    result = subprocess.run(
        [
            sys.executable,
            str(helper),
            "--queue",
            str(tmp_path / "queue"),
            "https://bad.test/?key=secret",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "secret" not in result.stderr


def test_missing_helper_leaves_no_broken_desktop(handler):
    nxm, _ = handler
    nxm.plugin_dir = nxm.home / "missing"
    with pytest.raises(ModsError):
        nxm.set_enabled(True)
    assert not (nxm.home / ".local/share/applications/decky-mods-nxm.desktop").exists()
