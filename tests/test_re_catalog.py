"""Every published RE catalog entry reaches the real adapter and reversible engine."""

from pathlib import Path

import pytest
from decky_mods.adapters import plan_files
from decky_mods.catalog import load_catalog
from decky_mods.deployment import Deployment

ROOT = Path(__file__).resolve().parents[1]
RESIDENT = [game for game in load_catalog(ROOT) if game["series"] == "resident-evil"]


@pytest.mark.parametrize("entry", RESIDENT, ids=lambda game: game["id"])
def test_each_real_resident_catalog_mapping_roundtrip(entry, tmp_path):
    root, staging = tmp_path / "game", tmp_path / "archive"
    root.mkdir()
    staging.mkdir()
    game = {
        **entry,
        "installed": True,
        "path": str(root),
        "app_id": entry["steam_app_ids"][0],
        "build_id": "1",
        "running": False,
    }
    if entry["adapter"] == "re_legacy":
        relative = entry["adapter_config"]["legacy_root"] + "/assets/sample.arc"
        before = b"original resource"
        target = root / relative
        target.parent.mkdir(parents=True)
        target.write_bytes(before)
    else:
        assert entry["adapter"] == "reframework"
        (root / "dinput8.dll").write_bytes(b"loader fixture")
        (root / "re2_fw_config.txt").write_text("LooseFileLoader_Enabled=true\n")
        relative, before = "natives/stm/character/model.mesh.1", None
        target = root / relative
    source = staging / relative
    source.parent.mkdir(parents=True)
    source.write_bytes(b"mod resource")
    mapping = plan_files(game, staging)
    assert mapping["blocked_reason"] is None
    assert mapping["files"]
    engine = Deployment(tmp_path / "state")
    plan = engine.prepare(game, "Catalog MOD", staging, mapping)
    mod = engine.install(game, plan["id"], allow_conflicts=True)
    assert target.read_bytes() == b"mod resource"
    engine.set_enabled(game, mod["id"], False)
    assert (target.read_bytes() if target.exists() else None) == before
    engine.set_enabled(game, mod["id"], True)
    assert target.read_bytes() == b"mod resource"
    engine.uninstall(game, mod["id"])
    assert (target.read_bytes() if target.exists() else None) == before
    assert engine.list_mods(game["id"]) == []
