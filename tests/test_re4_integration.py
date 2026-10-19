"""A researched catalog entry must work through the whole deployment pipeline."""

from pathlib import Path

from decky_mods.adapters import plan_files
from decky_mods.catalog import load_catalog
from decky_mods.deployment import Deployment

ROOT = Path(__file__).resolve().parents[1]


def test_real_re4_catalog_pak_installs_disables_and_uninstalls(tmp_path):
    entry = next(game for game in load_catalog(ROOT) if game["id"] == "residentevil42023")
    install = tmp_path / "RESIDENT EVIL 4  BIOHAZARD RE4"
    install.mkdir()
    (install / "dinput8.dll").write_bytes(b"synthetic installed loader fixture")
    (install / "re_chunk_000.pak").write_bytes(b"official base archive")
    (install / "re_chunk_000.pak.patch_001.pak").write_bytes(b"official update archive")
    selected = {
        **entry,
        "installed": True,
        "path": str(install),
        "app_id": entry["steam_app_ids"][0],
        "build_id": "123",
        "running": False,
    }
    assert "pak_prefix" not in selected
    extracted = tmp_path / "downloaded"
    extracted.mkdir()
    (extracted / "re_chunk_000.pak.patch_000.pak").write_bytes(b"downloaded mod bytes")

    mapping = plan_files(selected, extracted)
    assert mapping["blocked_reason"] is None
    assert mapping["files"][0]["kind"] == "re_pak"
    engine = Deployment(tmp_path / "state")
    plan = engine.prepare(selected, "Real catalog RE4 MOD", extracted, mapping)
    assert plan["can_install"]
    mod = engine.install(selected, plan["id"])
    deployed = install / "re_chunk_000.pak.patch_002.pak"
    assert deployed.read_bytes() == b"downloaded mod bytes"
    assert not (install / "re_chunk_000.pak.patch_000.pak").exists()

    engine.set_enabled(selected, mod["id"], False)
    assert not deployed.exists()
    assert not engine.list_mods(selected["id"])[0]["enabled"]
    engine.set_enabled(selected, mod["id"], True)
    assert deployed.read_bytes() == b"downloaded mod bytes"
    engine.uninstall(selected, mod["id"])
    assert not deployed.exists()
    assert engine.list_mods(selected["id"]) == []
    assert (install / "dinput8.dll").read_bytes() == b"synthetic installed loader fixture"
    assert (install / "re_chunk_000.pak").read_bytes() == b"official base archive"
    assert (install / "re_chunk_000.pak.patch_001.pak").read_bytes() == b"official update archive"
    assert list(install.rglob(".deckymods-*")) == []
