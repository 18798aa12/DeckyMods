"""Repeated desktop callbacks reuse an active download and its chosen installation mode."""

import threading

import pytest

from tests import test_service

service = test_service.service


@pytest.mark.parametrize("mode", ["auto", "game_root"])
def test_repeated_nxm_reuses_downloading_and_ready_job(service, monkeypatch, mode):
    instance, game, _ = service
    if mode == "game_root":
        instance.discovery.game = {**game, "adapter": "catalog", "support": "catalog"}
    waiting = instance.begin_download(game["id"], 1, 2, mode)
    started, release = threading.Event(), threading.Event()
    downloads = []
    original = instance.nexus.download

    def download(*args):
        downloads.append(True)
        started.set()
        assert release.wait(5)
        return original(*args)

    monkeypatch.setattr(instance.nexus, "download", download)
    first = instance.accept_nxm("nxm://valid")
    try:
        assert started.wait(5)
        repeated = instance.accept_nxm("nxm://valid")
        assert repeated["id"] == first["id"] == waiting["id"]
        assert len(instance.get_jobs()) == 1
    finally:
        release.set()
    ready = test_service.wait_job(instance, first["id"])
    assert ready["phase"] == "ready", ready
    repeated = instance.accept_nxm("nxm://valid")
    assert repeated["id"] == first["id"]
    assert repeated["plan_id"] == ready["plan_id"]
    assert len(instance.get_jobs()) == len(downloads) == 1
    assert instance.jobs.get(first["id"])["install_mode"] == mode


def test_stale_waiting_job_with_same_numeric_identity_does_not_block_other_game(service):
    instance, game, _ = service
    stale = instance.jobs.create(
        "removed-game", "Old", phase="awaiting_browser", identity={"mod_id": 1, "file_id": 2}
    )
    accepted = instance.accept_nxm("nxm://valid")
    assert accepted["id"] != stale["id"]
    assert accepted["game_id"] == game["id"]
    assert test_service.wait_job(instance, accepted["id"])["phase"] == "ready"
    assert instance.jobs.get(stale["id"])["phase"] == "awaiting_browser"
