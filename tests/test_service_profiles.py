"""Explicit routes survive local and browser handoff without widening legacy auto mode."""

import json
import zipfile

import pytest
from decky_mods.errors import ModsError
from decky_mods.install_guides import InstallGuides

from tests.test_install_guides import guide, write_guides
from tests.test_service import wait_job

pytest_plugins = ["tests.test_service"]


@pytest.fixture
def profile_service(service, tmp_path):
    instance, game, home = service
    instance.discovery.game = {**game, "steam_app_ids": ["413150"], "app_id": "413150"}
    (tmp_path / "guides").mkdir()
    write_guides(tmp_path / "guides", [guide()])
    instance.install_guides = InstallGuides(tmp_path / "guides")
    from pathlib import Path

    (Path(game["path"]) / "StardewModdingAPI.dll").write_bytes(b"synthetic loader")
    archive = home / "Downloads/pack.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr(
            "Example/manifest.json",
            json.dumps(
                {
                    "Name": "Example",
                    "Version": "1.0",
                    "UniqueID": "Example.Pack",
                    "ContentPackFor": {"UniqueID": "Pathoschild.ContentPatcher"},
                }
            ),
        )
        output.writestr("Example/content.json", "{}")
    return instance, game, archive


def test_selected_profile_import_is_reversible_and_default_mode_does_not_change(profile_service):
    instance, game, archive = profile_service
    result = instance.get_install_guide(game["id"])
    assert any(m["install_mode"] == "method:profile-smapi" for m in result["methods"])
    job = instance.import_archive(game["id"], str(archive), "Content pack", "method:profile-smapi")
    ready = wait_job(instance, job["id"])
    plan = instance.get_plan(ready["plan_id"])
    assert plan["can_install"], plan
    assert "Mods/Example/content.json" in plan["targets"]
    instance.install_plan(plan["id"], False)
    assert wait_job(instance, job["id"])["phase"] == "complete"
    mod = instance.get_game(game["id"])["mods"][0]
    instance.set_mod_enabled(game["id"], mod["id"], False)
    instance.set_mod_enabled(game["id"], mod["id"], True)
    instance.uninstall_mod(game["id"], mod["id"])
    assert instance.get_game(game["id"])["mods"] == []
    old = instance.import_archive(game["id"], str(archive), "Default")
    default_plan = instance.get_plan(wait_job(instance, old["id"])["plan_id"])
    assert not default_plan["can_install"]


def test_browser_handoff_preserves_profile_and_rejects_changing_method(profile_service):
    instance, game, _ = profile_service
    task = instance.begin_download(game["id"], 1, 2, "method:profile-smapi")
    assert task["phase"] == "awaiting_browser"
    with pytest.raises(ModsError, match="先选择游戏"):
        instance.accept_nxm("nxm://valid", "method:profile-smapi")
    job = instance.accept_nxm("nxm://valid")
    assert instance.jobs.get(job["id"])["install_mode"] == "method:profile-smapi"
    wait_job(instance, job["id"])


def test_wrong_or_external_method_never_creates_a_task(profile_service):
    instance, game, archive = profile_service
    for method in ("method:profile-cyberpunk-archive", "method:manual-test", "method:../../escape"):
        with pytest.raises(ModsError):
            instance.import_archive(game["id"], str(archive), "Wrong", method)
    assert instance.get_jobs() == []
