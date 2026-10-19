import json
import time
import zipfile
from pathlib import Path

import pytest
from decky_mods.errors import ModsError
from decky_mods.service import Service


class Discovery:
    def __init__(self, game):
        self.game = game
        self.issues = ()

    def discover(self):
        return [dict(self.game)]

    def resolve(self, game_id):
        if game_id != self.game["id"] or not self.game["installed"]:
            raise ModsError("未安装")
        return dict(self.game)


class Nexus:
    premium = False

    def status(self):
        return {
            "connected": True,
            "name": "Tester",
            "premium": self.premium,
            "user_id": 12,
            "error": None,
        }

    def bind(self, key):
        return self.status()

    def disconnect(self):
        return {**self.status(), "connected": False}

    def resolve(self, domain, reference):
        return {
            "mod_id": 1,
            "name": "Example",
            "author": "Author",
            "summary": "Summary",
            "page_url": f"https://www.nexusmods.com/{domain}/mods/1",
            "files": [{"file_id": 2, "name": "Example", "version": "1", "primary": True}],
        }

    def browser_url(self, domain, mod, file):
        return f"https://www.nexusmods.com/{domain}/mods/{mod}?tab=files&file_id={file}"

    def parse_nxm(self, uri):
        if uri != "nxm://valid":
            raise ModsError("无效授权")
        return {
            "domain": "stellarblade",
            "mod_id": 1,
            "file_id": 2,
            "user_id": 12,
            "key": "private",
            "expires": 9999999999,
        }

    def download(self, domain, mod, file, destination, cancel, progress, nxm_uri=None):
        with zipfile.ZipFile(destination, "w") as archive:
            archive.writestr("Test.pak", b"payload")
        progress(destination.stat().st_size, destination.stat().st_size)


class Handler:
    def status(self):
        return {"enabled": False, "supported": False, "previous": None, "message": None}

    def set_enabled(self, enabled):
        return {**self.status(), "enabled": enabled}

    def drain(self):
        return []

    def close(self):
        pass


@pytest.fixture
def service(tmp_path):
    home = tmp_path / "home"
    (home / "Downloads").mkdir(parents=True)
    root = tmp_path / "Game"
    root.mkdir()
    game = {
        "id": "stellar-blade",
        "name": "Stellar Blade",
        "series": "stellar-blade",
        "series_name": "剑星",
        "nexus_domain": "stellarblade",
        "steam_app_ids": ["3489700"],
        "adapter": "ue_pak",
        "adapter_config": {"pak_dir": "SB/Content/Paks/~mods"},
        "support": "automatic",
        "requirements": [],
        "sources": [],
        "installed": True,
        "path": str(root),
        "app_id": "3489700",
        "build_id": "1",
        "running": False,
    }
    (root / "SB/Content/Paks").mkdir(parents=True)
    instance = Service(
        Path(__file__).resolve().parents[1],
        tmp_path / "private",
        home=home,
        discovery=Discovery(game),
        nexus=Nexus(),
        handler=Handler(),
    )
    yield instance, game, home
    instance.close()


def wait_job(instance, job_id):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        job = next(item for item in instance.get_jobs() if item["id"] == job_id)
        if job["phase"] in {"ready", "complete", "failed", "cancelled"}:
            return job
        time.sleep(0.01)
    raise AssertionError("job did not finish")


def test_launch_options_preserve_existing_framegen_and_restore(service):
    instance, game, _ = service
    instance.discovery.game = {**game, "adapter": "reframework"}
    (Path(game["path"]) / "dinput8.dll").write_bytes(b"loader")
    setup = instance.get_launch_setup(game["id"])
    assert setup["required"] is True
    original = 'WINEDLLOVERRIDES="dxgi=n,b" %command% -windowed'
    change = instance.prepare_launch_options(game["id"], original)
    assert change["changed"] is True
    assert "dxgi=n,b;dinput8.dll=n,b" in change["after"]
    assert change["after"].endswith("%command% -windowed")
    applied = instance.finish_launch_options(game["id"], change["id"], change["after"])
    assert applied["backup_available"] is True
    restore = instance.prepare_launch_options(game["id"], change["after"], True)
    assert restore["after"] == original
    restored = instance.finish_launch_options(game["id"], restore["id"], original)
    assert restored["auto_enabled"] is False


def test_launch_options_status_for_unknown_adapter_and_automatic_switch(service):
    instance, game, _ = service
    assert instance.get_launch_setup(game["id"])["supported"] is False
    instance.discovery.game = {**game, "adapter": "reframework"}
    assert instance.set_launch_auto(game["id"], False)["auto_enabled"] is False


def test_launch_options_do_not_write_during_unresolved_file_recovery(service):
    instance, game, _ = service
    instance.discovery.game = {**game, "adapter": "reframework"}
    (Path(game["path"]) / "dinput8.dll").write_bytes(b"loader")
    instance.recovery_errors = {game["id"]: "恢复失败"}
    with pytest.raises(ModsError, match="恢复"):
        instance.prepare_launch_options(game["id"], "")


def test_resident_resource_install_prepares_settings_without_managing_them_as_mod_files(service):
    instance, game, home = service
    current = {
        **game,
        "id": "residentevil7",
        "series": "resident-evil",
        "adapter": "reframework",
        "adapter_config": {},
        "app_id": "418370",
    }
    instance.discovery.game = current
    root = Path(game["path"])
    (root / "dinput8.dll").write_bytes(b"loader")
    (root / "re2_fw_config.txt").write_text("Other=keep\nLooseFileLoader_Enabled=false\n")
    source = home / "Downloads/resource.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("natives/stm/character/model.mesh.123", b"resource")
    task = instance.import_archive(current["id"], str(source), "Resource")
    ready = wait_job(instance, task["id"])
    plan = instance.get_plan(ready["plan_id"])
    assert plan["can_install"]
    assert plan["config_requirements"] == ["LooseFileLoader_Enabled"]
    instance.install_plan(plan["id"], False)
    assert wait_job(instance, task["id"])["phase"] == "complete"
    assert instance.get_resident_status(current["id"])["loose_enabled"]
    with pytest.raises(ModsError, match="禁用"):
        instance.restore_resident_settings(current["id"])
    mod = instance.get_game(current["id"])["mods"][0]
    # REFramework may rewrite other global preferences during a later game session.
    with (root / "re2_fw_config.txt").open("a") as stream:
        stream.write("WindowOption=new\n")
    instance.set_mod_enabled(current["id"], mod["id"], False)
    assert not (root / "natives/stm/character/model.mesh.123").exists()
    assert "WindowOption=new" in (root / "re2_fw_config.txt").read_text()


def test_local_archive_install_toggle_uninstall_complete_flow(service):
    instance, game, home = service
    source = home / "Downloads" / "mod.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("Test.pak", b"payload")
    task = instance.import_archive(game["id"], str(source), "Local Mod")
    job = wait_job(instance, task["id"])
    assert job["phase"] == "ready", job
    plan = instance.get_plan(job["plan_id"])
    assert plan["can_install"]
    install = wait_job(instance, instance.install_plan(plan["id"], False)["id"])
    assert install["phase"] == "complete", install
    target = Path(game["path"], "SB/Content/Paks/~mods/Test.pak")
    assert target.read_bytes() == b"payload"
    mod = instance.get_game(game["id"])["mods"][0]
    instance.set_mod_enabled(game["id"], mod["id"], False)
    assert not target.exists()
    instance.set_mod_enabled(game["id"], mod["id"], True)
    instance.uninstall_mod(game["id"], mod["id"])
    assert not target.exists()


def test_free_member_browser_handoff_reuses_job_and_never_exposes_grant(service):
    instance, game, _ = service
    info = instance.resolve_mod(game["id"], "1")
    assert info["game_id"] == game["id"]
    waiting = instance.begin_download(game["id"], 1, 2)
    assert waiting["phase"] == "awaiting_browser"
    assert "nexusmods.com" in waiting["browser_url"]
    received = instance.accept_nxm("nxm://valid")
    assert received["id"] == waiting["id"]
    assert wait_job(instance, received["id"])["phase"] == "ready"
    assert "private" not in json.dumps(instance.get_status())


def test_cancel_waiting_job_blocks_install_and_premium_background_download(service):
    instance, game, _ = service
    waiting = instance.begin_download(game["id"], 1, 2)
    assert instance.cancel_job(waiting["id"])["phase"] == "cancelled"
    instance.nexus.premium = True
    task = instance.begin_download(game["id"], 1, 2)
    done = wait_job(instance, task["id"])
    assert done["phase"] == "ready"
    instance.cancel_job(done["id"])
    with pytest.raises(ModsError):
        instance.install_plan(done["plan_id"], False)


@pytest.mark.parametrize("name", ["other.zip", ".hidden.zip"])
def test_archive_import_rejects_outside_home_and_hidden_files(service, tmp_path, name):
    instance, game, home = service
    source = tmp_path / name if name == "other.zip" else home / "Downloads" / name
    source.write_bytes(b"bad")
    with pytest.raises(ModsError):
        instance.import_archive(game["id"], str(source), "Invalid")


def test_game_wrong_reference_file_and_unknown_jobs_rejected(service):
    instance, game, _ = service
    with pytest.raises(ModsError):
        instance.begin_download(game["id"], 1, 999)
    with pytest.raises(ModsError):
        instance.get_game("other")
    with pytest.raises(ModsError):
        instance.cancel_job("unknown")


def test_account_actions_handler_and_stopped_queue_poll(service):
    instance, _, _ = service
    assert instance.bind_account("user-key")["connected"]
    assert not instance.disconnect_account()["connected"]
    assert instance.set_nxm_handler(True)["enabled"]
    instance.poll_inbox()
    assert len(instance.list_games()) == 1


def test_nxm_receiver_intent_survives_native_update_unload(service):
    instance, _, home = service
    instance.set_nxm_handler(True)
    calls = []

    class ResumedHandler(Handler):
        def set_enabled(self, enabled):
            calls.append(enabled)
            return super().set_enabled(enabled)

    reopened = Service(
        instance.plugin_dir,
        instance.directory,
        home=home,
        discovery=instance.discovery,
        nexus=Nexus(),
        handler=ResumedHandler(),
    )
    try:
        assert calls == [True]
    finally:
        reopened.close()


def test_generic_root_requires_explicit_mode_and_preserves_original_files(service):
    instance, game, home = service
    instance.discovery.game = {**game, "adapter": "catalog", "support": "catalog"}
    root = Path(game["path"])
    (root / "texture.png").write_bytes(b"original")
    source = home / "Downloads/root.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("texture.png", b"modded")
        archive.writestr(
            "modinfo.ini",
            "name=Root Mod\nauthor=Example\nversion=1.2\ndescription=Local instructions",
        )
    blocked = wait_job(instance, instance.import_archive(game["id"], str(source), "Root")["id"])
    assert not instance.get_plan(blocked["plan_id"])["can_install"]
    job = wait_job(
        instance, instance.import_archive(game["id"], str(source), "Root", "game_root")["id"]
    )
    plan = instance.get_plan(job["plan_id"])
    assert plan["can_install"] and plan["conflicts"] == ["texture.png"]
    assert plan["targets"] == ["modinfo.ini", "texture.png"]
    assert wait_job(instance, instance.install_plan(plan["id"], True)["id"])["phase"] == "complete"
    mod = instance.get_game(game["id"])["mods"][0]
    assert "details" not in mod
    details = instance.get_mod_details(game["id"], mod["id"])
    assert details["author"] == "Example" and "Local instructions" in details["description"]
    instance.set_mod_enabled(game["id"], mod["id"], False)
    assert (root / "texture.png").read_bytes() == b"original"
    instance.set_mod_enabled(game["id"], mod["id"], True)
    instance.uninstall_mod(game["id"], mod["id"])
    assert (root / "texture.png").read_bytes() == b"original"


@pytest.mark.parametrize("mode", [True, None, "root", "../game"])
def test_reject_invalid_install_mode_before_creating_jobs(service, mode):
    instance, game, _ = service
    with pytest.raises(ModsError, match="安装模式"):
        instance.begin_download(game["id"], 1, 2, mode)
    assert instance.get_jobs() == []


def test_generic_root_mode_cannot_bypass_reviewed_adapter(service):
    instance, game, _ = service
    with pytest.raises(ModsError, match="已适配"):
        instance.begin_download(game["id"], 1, 2, "game_root")


def test_browser_handoff_keeps_explicit_root_mode(service):
    instance, game, _ = service
    instance.discovery.game = {**game, "adapter": "catalog", "support": "catalog"}
    waiting = instance.begin_download(game["id"], 1, 2, "game_root")
    received = instance.accept_nxm("nxm://valid")
    assert received["id"] == waiting["id"]
    ready = wait_job(instance, received["id"])
    assert instance.get_plan(ready["plan_id"])["can_install"]
    assert instance.get_plan(ready["plan_id"])["targets"] == ["Test.pak"]


def test_missing_installed_mod_details_rejected(service):
    instance, game, _ = service
    with pytest.raises(ModsError, match="MOD"):
        instance.get_mod_details(game["id"], "unknown")


def test_manual_game_root_cannot_move_existing_mods_or_pending_jobs(service):
    instance, game, home = service
    instance.discovery.game = {**game, "adapter": "catalog", "support": "catalog"}
    manual = home / "Games/Custom"
    manual.mkdir(parents=True)
    (manual / "game.exe").write_bytes(b"MZ")
    view = instance.set_game_root(game["id"], "manual", str(manual))
    assert view["game"]["manual_root"] and view["game"]["path"] == str(manual)
    source = home / "Downloads/manual.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("mod.ini", "enabled=true")
    task = wait_job(
        instance, instance.import_archive(game["id"], str(source), "Manual", "game_root")["id"]
    )
    with pytest.raises(ModsError, match="任务"):
        instance.set_game_root(game["id"], "auto", "")
    instance.install_plan(task["plan_id"], False)
    assert wait_job(instance, task["id"])["phase"] == "complete"
    with pytest.raises(ModsError, match="MOD"):
        instance.set_game_root(game["id"], "auto", "")
    assert (manual / "mod.ini").exists()
    mod = instance.get_game(game["id"])["mods"][0]
    instance.uninstall_mod(game["id"], mod["id"])
    assert not (manual / "mod.ini").exists()
    assert not instance.set_game_root(game["id"], "auto", "")["game"]["manual_root"]


def test_root_nxm_requires_matching_explicit_game_and_rejects_reinterpreting_jobs(service):
    instance, game, _ = service
    instance.discovery.game = {**game, "adapter": "catalog", "support": "catalog"}
    with pytest.raises(ModsError, match="选择游戏"):
        instance.accept_nxm("nxm://valid", "game_root")
    instance.discovery.game = {**instance.discovery.game, "nexus_domain": "other"}
    with pytest.raises(ModsError, match="不同"):
        instance.accept_nxm("nxm://valid", "game_root", game["id"])
    instance.discovery.game = {**instance.discovery.game, "nexus_domain": "stellarblade"}
    instance.begin_download(game["id"], 1, 2)
    with pytest.raises(ModsError, match="模式不同"):
        instance.accept_nxm("nxm://valid", "game_root", game["id"])
