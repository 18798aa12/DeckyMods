"""Synthetic local ZIP flows use the same reversible engine for discovered games."""

import zipfile

import pytest
from decky_mods.catalog import load_catalog
from decky_mods.errors import ModsError
from decky_mods.service import Service
from decky_mods.steam import SteamDiscovery

from tests.test_service import Handler, Nexus, wait_job
from tests.test_steam_library import ROOT, installed


@pytest.fixture
def dynamic_service(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / "Downloads").mkdir(parents=True)
    root = installed(home / ".local/share/Steam", "390000001", "Synthetic Unreal title")
    # Unreal titles need not contain a top-level EXE for validated Steam discovery.
    (root / "b1/Binaries/Win64").mkdir(parents=True)
    (root / "b1/Binaries/Win64/b1.exe").write_bytes(b"MZgame")
    monkeypatch.setattr("decky_mods.steam._running_apps", lambda candidates: (set(), set()))
    nexus = Nexus()

    def unexpected(*args, **kwargs):
        pytest.fail("discovered game must not attempt an unverified Nexus mapping")

    monkeypatch.setattr(nexus, "resolve", unexpected)
    monkeypatch.setattr(nexus, "download", unexpected)
    service = Service(
        ROOT,
        tmp_path / "state",
        home=home,
        discovery=SteamDiscovery(load_catalog(ROOT), home),
        nexus=nexus,
        handler=Handler(),
    )
    yield service, root, home
    service.close()


@pytest.mark.parametrize("operation", ["resolve", "download"])
def test_unmapped_games_block_nexus_before_any_network_call(dynamic_service, operation):
    service, _, _ = dynamic_service
    with pytest.raises(ModsError, match="本地.*压缩包|本地.*ZIP"):
        if operation == "resolve":
            service.resolve_mod("steam-390000001", "123")
        else:
            service.begin_download("steam-390000001", 123, 456, "game_root")
    assert service.get_jobs() == []


def test_discovered_game_local_root_install_toggle_and_uninstall(dynamic_service):
    service, root, home = dynamic_service
    archive = home / "Downloads/local-mod.zip"
    (root / "settings.ini").write_bytes(b"original")
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("settings.ini", b"modified")
        output.writestr("b1/Content/Paks/~mods/example.pak", b"synthetic mod")
    job = service.import_archive("steam-390000001", str(archive), "Synthetic MOD", "game_root")
    ready = wait_job(service, job["id"])
    assert ready["phase"] == "ready", ready
    plan = service.get_plan(ready["plan_id"])
    assert plan["can_install"]
    assert plan["conflicts"] == ["settings.ini"]
    assert set(plan["targets"]) == {
        "settings.ini",
        "b1/Content/Paks/~mods/example.pak",
    }
    assert not (root / "b1/Content/Paks/~mods/example.pak").exists()
    service.install_plan(plan["id"], True)
    assert wait_job(service, job["id"])["phase"] == "complete"
    mod = service.get_game("steam-390000001")["mods"][0]
    assert (root / "settings.ini").read_bytes() == b"modified"
    service.set_mod_enabled("steam-390000001", mod["id"], False)
    assert (root / "settings.ini").read_bytes() == b"original"
    assert not (root / "b1/Content/Paks/~mods/example.pak").exists()
    service.set_mod_enabled("steam-390000001", mod["id"], True)
    assert (root / "b1/Content/Paks/~mods/example.pak").read_bytes() == b"synthetic mod"
    service.uninstall_mod("steam-390000001", mod["id"])
    assert (root / "settings.ini").read_bytes() == b"original"
    assert not (root / "b1/Content/Paks/~mods/example.pak").exists()
    assert service.get_game("steam-390000001")["mods"] == []


def test_discovered_game_still_requires_explicit_root_mode(dynamic_service):
    service, root, home = dynamic_service
    archive = home / "Downloads/local-mod.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("Data/example.bin", b"synthetic mod")
    job = service.import_archive("steam-390000001", str(archive), "Synthetic MOD")
    ready = wait_job(service, job["id"])
    plan = service.get_plan(ready["plan_id"])
    assert not plan["can_install"] and plan["blocked_reason"]
    assert not (root / "Data/example.bin").exists()
