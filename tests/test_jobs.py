"""Regressions for cancellation and chained scan-to-install scheduling."""

import threading

import pytest
from decky_mods.errors import ModsError
from decky_mods.jobs import Jobs


def test_cancelled_scan_cannot_publish_ready_plan(tmp_path):
    queue = Jobs(tmp_path / "tasks")
    try:
        job = queue.create("game", "mod", phase="scanning")
        queue.cancel(job["id"])
        queue.update(job["id"], phase="ready", plan_id="late-plan")
        row = queue.get(job["id"])
        assert row["phase"] == "cancelled"
        assert row["plan_id"] is None
    finally:
        queue.close()


def test_install_waits_for_ready_scan_worker_to_finish(tmp_path):
    queue = Jobs(tmp_path / "tasks")
    ready, release, installed = threading.Event(), threading.Event(), threading.Event()
    job = queue.create("game", "mod")

    def scan(cancel):
        queue.update(job["id"], phase="ready", plan_id="plan")
        ready.set()
        assert release.wait(3)

    def install(cancel):
        installed.set()
        queue.update(job["id"], phase="complete")

    try:
        queue.start(job["id"], scan)
        assert ready.wait(3)
        result = queue.start(job["id"], install, transition=("ready", "installing"))
        assert result["phase"] == "installing"
        assert not installed.is_set()
        release.set()
        queue.futures[job["id"]].result(timeout=3)
        assert installed.is_set()
        assert queue.get(job["id"])["phase"] == "complete"
    finally:
        release.set()
        queue.close()


def test_cancel_and_install_transition_are_mutually_exclusive(tmp_path):
    queue = Jobs(tmp_path / "tasks")
    try:
        job = queue.create("game", "mod", phase="ready", plan_id="plan")
        queue.cancel(job["id"])
        with pytest.raises(ModsError):
            queue.start(job["id"], lambda cancel: None, transition=("ready", "installing"))
        assert queue.get(job["id"])["phase"] == "cancelled"
    finally:
        queue.close()
