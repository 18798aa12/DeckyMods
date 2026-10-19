"""Busy games defer crash recovery without becoming permanent recovery failures."""

from pathlib import Path

import pytest

from tests import test_service
from tests.test_deployment import prepare

service = test_service.service


@pytest.mark.parametrize("busy", ["running", "updating"])
@pytest.mark.parametrize("configuration", [False, True])
def test_busy_game_recovery_resumes_after_steam_becomes_idle(
    service, tmp_path, busy, configuration
):
    instance, game, _ = service
    target = Path(game["path"]) / "original.txt"
    target.write_bytes(b"original")
    engine = instance.resident.engine if configuration else instance.engine

    def interrupted(index, name):
        raise KeyboardInterrupt("simulated power loss")

    engine.fault = interrupted
    plan = prepare(engine, game, tmp_path, target="original.txt", payload=b"interrupted")
    with pytest.raises(KeyboardInterrupt):
        engine.install(game, plan["id"], True)
    pending = engine.db.pending(game["id"])
    assert pending and target.read_bytes() == b"interrupted"

    instance.discovery.game = {**game, busy: True}
    instance.recover_all()
    assert instance.get_game(game["id"])["recovery_error"] is None
    assert engine.db.pending(game["id"]) == pending
    assert target.read_bytes() == b"interrupted"

    instance.discovery.game = {**game, busy: False}
    instance.recover_all()
    assert not engine.db.pending(game["id"])
    assert target.read_bytes() == b"original"
