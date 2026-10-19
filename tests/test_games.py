from __future__ import annotations

import json
from pathlib import Path

import pytest
from decky_mods.adapters import plan_files
from decky_mods.catalog import load_catalog
from decky_mods.errors import ModsError
from decky_mods.steam import SteamDiscovery

ROOT = Path(__file__).resolve().parents[1]


def game(game_id: str, path: Path) -> dict:
    entry = next(item for item in load_catalog(ROOT) if item["id"] == game_id)
    return {
        **entry,
        "installed": True,
        "path": str(path),
        "app_id": entry["steam_app_ids"][0],
        "build_id": "123",
        "running": False,
    }


def put(root: Path, name: str, data: bytes = b"payload") -> None:
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def manifest(root: Path, app_id: str, install_dir: str, extra: str = "") -> None:
    put(
        root,
        f"steamapps/appmanifest_{app_id}.acf",
        (
            f'"AppState" {{ "appid" "{app_id}" "installdir" "{install_dir}" '
            f'"buildid" "123" {extra} }}'
        ).encode(),
    )


def test_catalog_has_at_least_50_real_series_and_re_title_variants() -> None:
    items = load_catalog(ROOT)
    assert len({item["series"] for item in items}) >= 50
    assert len({item["id"] for item in items}) == len(items)
    resident = [item for item in items if item["series"] == "resident-evil"]
    assert len(resident) >= 13
    assert {"254700", "2050650"} <= {x for item in resident for x in item["steam_app_ids"]}
    assert all(item["sources"] and item["requirements"] for item in items)
    assert all("hardware" in item["validation"] for item in items)


def test_catalog_rejects_untrusted_target_path(tmp_path: Path) -> None:
    entries = load_catalog(ROOT)
    entries[0]["adapter_config"] = {"pak_dir": "../../escape"}
    (tmp_path / "data").mkdir()
    (tmp_path / "data/games.json").write_text(json.dumps(entries))
    with pytest.raises(ModsError):
        load_catalog(tmp_path)


def test_discovery_default_and_sdcard_libraries(tmp_path: Path) -> None:
    home = tmp_path / "home"
    steam = home / ".local/share/Steam"
    sd = tmp_path / "SD card/SteamLibrary"
    put(
        steam,
        "steamapps/libraryfolders.vdf",
        (
            '"libraryfolders" { "0" { "path" "' + str(steam) + '" } '
            '"1" { "path" "' + str(sd) + '" } }'
        ).encode(),
    )
    manifest(steam, "3489700", "StellarBlade")
    manifest(sd, "2050650", "RESIDENT EVIL 4  BIOHAZARD RE4")
    (steam / "steamapps/common/StellarBlade").mkdir(parents=True)
    (sd / "steamapps/common/RESIDENT EVIL 4  BIOHAZARD RE4").mkdir(parents=True)
    legacy = home / ".steam"
    legacy.mkdir()
    (legacy / "steam").symlink_to(steam, target_is_directory=True)
    discovered = SteamDiscovery(load_catalog(ROOT), home).discover()
    installed = [item for item in discovered if item["installed"]]
    assert len(installed) == 2
    assert {item["app_id"] for item in installed} == {"3489700", "2050650"}
    assert all(item["build_id"] == "123" for item in installed)
    assert all(item["path"] and not item["running"] for item in installed)


@pytest.mark.parametrize("install_dir", ["../outside", "/absolute", "nested/game", ""])
def test_discovery_rejects_manifest_path_escape(tmp_path: Path, install_dir: str) -> None:
    steam = tmp_path / ".local/share/Steam"
    manifest(steam, "3489700", install_dir)
    assert not SteamDiscovery(load_catalog(ROOT), tmp_path).resolve_optional("stellarblade")


def test_discovery_rejects_common_child_symlink_escape(tmp_path: Path) -> None:
    steam = tmp_path / ".local/share/Steam"
    manifest(steam, "3489700", "StellarBlade")
    common = steam / "steamapps/common"
    common.mkdir()
    outside = tmp_path / "private"
    outside.mkdir()
    (common / "StellarBlade").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ModsError, match="安装"):
        SteamDiscovery(load_catalog(ROOT), tmp_path).resolve("stellarblade")


def test_discovery_running_manifest_and_missing_game(tmp_path: Path) -> None:
    steam = tmp_path / ".local/share/Steam"
    manifest(steam, "3489700", "StellarBlade", '"Running" "1"')
    (steam / "steamapps/common/StellarBlade").mkdir(parents=True)
    assert SteamDiscovery(load_catalog(ROOT), tmp_path).resolve("stellarblade")["running"]
    with pytest.raises(ModsError):
        SteamDiscovery(load_catalog(ROOT), tmp_path).resolve("not-a-game")


def test_stellar_triplet_maps_atomically_and_does_not_mutate_game(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    install.mkdir()
    selected = game("stellarblade", install)
    original = json.dumps(selected, sort_keys=True)
    for suffix in ["pak", "ucas", "utoc"]:
        put(archive, f"MyMod/SB/Content/Paks/~mods/Costume_P.{suffix}")
    put(archive, "MyMod/readme.txt")
    result = plan_files(selected, archive)
    assert result["blocked_reason"] is None
    assert {item["target"] for item in result["files"]} == {
        f"SB/Content/Paks/~mods/Costume_P.{suffix}" for suffix in ["pak", "ucas", "utoc"]
    }
    assert json.dumps(selected, sort_keys=True) == original


@pytest.mark.parametrize(
    "files",
    [
        [],
        ["a.utoc"],
        ["a.pak", "a.ucas"],
        ["a.pak", "b.utoc", "b.ucas"],
        ["CodeVein/Content/Paks/~mods/a.pak"],
        ["LogicMods/a.pak"],
        ["foo.exe"],
        ["OptionA/a.pak", "OptionB/b.pak"],
    ],
)
def test_stellar_rejects_incomplete_unknown_or_wrong_game_packages(
    tmp_path: Path, files: list[str]
) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    install.mkdir()
    archive.mkdir()
    for name in files:
        put(archive, name)
    result = plan_files(game("stellarblade", install), archive)
    assert result["blocked_reason"]
    assert not result["files"]


def test_adapter_rejects_archive_symlink(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    install.mkdir()
    archive.mkdir()
    outside = tmp_path / "outside.pak"
    outside.write_bytes(b"secret")
    (archive / "a.pak").symlink_to(outside)
    with pytest.raises(ModsError):
        plan_files(game("stellarblade", install), archive)


def test_reframework_requires_loader_and_preserves_script_tree(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    install.mkdir()
    put(archive, "Mod/reframework/autorun/example/init.lua")
    selected = game("residentevil42023", install)
    assert plan_files(selected, archive)["blocked_reason"]
    put(install, "dinput8.dll")
    result = plan_files(selected, archive)
    assert result["blocked_reason"] is None
    assert result["files"][0]["target"] == "reframework/autorun/example/init.lua"
    assert any("WINEDLLOVERRIDES" in item for item in result["requirements"])


def test_re_natives_requires_explicit_modern_loose_loader_config(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    install.mkdir()
    put(install, "dinput8.dll")
    put(archive, "natives/stm/character/model.mesh.123")
    selected = game("residentevil42023", install)
    assert plan_files(selected, archive)["blocked_reason"]
    put(install, "re4_fw_config.txt", b"LooseFileLoader_Enabled=false\n")
    assert plan_files(selected, archive)["blocked_reason"]
    put(install, "re4_fw_config.txt", b"LooseFileLoader_Enabled=true\n")
    assert plan_files(selected, archive)["blocked_reason"]
    put(install, "re2_fw_config.txt", b"LooseFileLoader_Enabled=false\n")
    proposed = plan_files(selected, archive)
    assert proposed["blocked_reason"] is None
    assert proposed["config_requirements"] == ["LooseFileLoader_Enabled"]
    put(install, "re2_fw_config.txt", b"LooseFileLoader_Enabled=true\n")
    result = plan_files(selected, archive)
    assert result["blocked_reason"] is None
    assert result["files"][0]["target"].startswith("natives/stm/")


def test_classic_resident_and_catalog_games_block_deployment(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    install.mkdir()
    put(archive, "natives/stm/file.bin")
    for ident in ["residentevil4", "baldursgate3"]:
        result = plan_files(game(ident, install), archive)
        assert result["blocked_reason"] and not result["files"]


def test_reject_game_running_and_uninstalled(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    put(archive, "a.pak")
    selected = game("stellarblade", tmp_path)
    for changes in [{"running": True}, {"installed": False}, {"path": None}]:
        with pytest.raises(ModsError):
            plan_files({**selected, **changes}, archive)
