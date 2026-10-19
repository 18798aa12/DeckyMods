"""Paused game downloads do not lock unrelated plugin upgrades indefinitely."""

import pytest
from decky_mods.errors import ModsError

pytest_plugins = ["tests.test_service"]


@pytest.mark.parametrize("active", [False, True, None])
def test_plugin_update_uses_active_maintenance_and_conservative_legacy_fallback(
    service, monkeypatch, active
):
    instance, game, _ = service
    instance.discovery.game = {
        **game,
        "updating": True,
        **({"update_active": active} if active is not None else {}),
    }
    prepared = {"version": "9.0.0", "artifact": "synthetic", "sha256": "0" * 64}
    monkeypatch.setattr(instance.updates, "prepare", lambda: prepared)
    if active is False:
        assert instance.prepare_update() == prepared
    else:
        with pytest.raises(ModsError, match="Steam"):
            instance.prepare_update()


def test_running_game_still_blocks_plugin_update_even_with_paused_download(service):
    instance, game, _ = service
    instance.discovery.game = {**game, "running": True, "updating": True, "update_active": False}
    with pytest.raises(ModsError, match="退出游戏"):
        instance.prepare_update()
