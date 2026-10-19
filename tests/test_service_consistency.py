"""Resource prerequisites and enabled MODs share one serialized state transition."""

import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from decky_mods.errors import ModsError

from tests import test_service

service = test_service.service


@pytest.mark.parametrize("action", ["install", "enable"])
def test_restore_cannot_disable_flags_during_resource_activation(service, monkeypatch, action):
    instance, original, home = service
    game = {
        **original,
        "id": "residentevil7",
        "series": "resident-evil",
        "adapter": "reframework",
        "adapter_config": {},
        "app_id": "418370",
    }
    instance.discovery.game = game
    root = Path(game["path"])
    (root / "dinput8.dll").write_bytes(b"synthetic loader")
    (root / "re2_fw_config.txt").write_text("LooseFileLoader_Enabled=false\n")
    archive = home / "Downloads/resource.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("natives/stm/character/model.mesh.123", b"resource")
    job = instance.import_archive(game["id"], str(archive), "Resource")
    ready = test_service.wait_job(instance, job["id"])
    mod_id = None
    if action == "enable":
        instance.install_plan(ready["plan_id"], False)
        assert test_service.wait_job(instance, job["id"])["phase"] == "complete"
        mod_id = instance.get_game(game["id"])["mods"][0]["id"]
        instance.set_mod_enabled(game["id"], mod_id, False)
        instance.restore_resident_settings(game["id"])

    prepared, release, attempted = threading.Event(), threading.Event(), threading.Event()
    original_prepare = instance._prepare_resource_flags

    def pause_after_flags(*args):
        original_prepare(*args)
        prepared.set()
        assert release.wait(5)

    monkeypatch.setattr(instance, "_prepare_resource_flags", pause_after_flags)
    original_restore = instance.resident.restore

    def observe_restore(current):
        attempted.set()
        return original_restore(current)

    monkeypatch.setattr(instance.resident, "restore", observe_restore)
    underlying = instance.engine.lock
    restoring = []

    class ObservedLock:
        def __enter__(self):
            if restoring and threading.get_ident() == restoring[0]:
                attempted.set()
            return underlying.__enter__()

        def __exit__(self, *args):
            return underlying.__exit__(*args)

    monkeypatch.setattr(instance.engine, "lock", ObservedLock())

    def restore():
        restoring.append(threading.get_ident())
        return instance.restore_resident_settings(game["id"])

    with ThreadPoolExecutor() as executor:
        activation = (
            executor.submit(instance.install_plan, ready["plan_id"], False)
            if action == "install"
            else executor.submit(instance.set_mod_enabled, game["id"], mod_id, True)
        )
        try:
            assert prepared.wait(5)
            restoration = executor.submit(restore)
            assert attempted.wait(5)
        finally:
            release.set()
        activation.result(timeout=5)
        with pytest.raises(ModsError, match="禁用"):
            restoration.result(timeout=5)
    assert test_service.wait_job(instance, job["id"])["phase"] == "complete"
    assert instance.get_resident_status(game["id"])["loose_enabled"]
    assert instance.get_game(game["id"])["mods"][0]["enabled"]
