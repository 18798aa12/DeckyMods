from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from decky_mods import steam
from decky_mods.adapters import plan_files
from decky_mods.catalog import load_catalog
from decky_mods.errors import ModsError
from decky_mods.steam import SteamDiscovery
from decky_mods.vdf import read_vdf

from tests.test_games import ROOT, game, manifest, put


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("id", "../bad"),
        ("name", ""),
        ("series", "bad/series"),
        ("steam_app_ids", ["0"]),
        ("steam_app_ids", [123]),
        ("steam_app_ids", []),
        ("adapter", "shell"),
        ("support", "tested"),
        ("support", "catalog"),
        ("sources", []),
        ("sources", ["http://example.com"]),
        ("requirements", []),
        ("adapter_config", {"shell": "rm"}),
        ("adapter_config", {"pak_dir": "/etc"}),
        ("adapter_config", {"pak_dir": "a\\b"}),
    ],
)
def test_invalid_catalog_fields_fail_closed(tmp_path: Path, key: str, value: object) -> None:
    items = load_catalog(ROOT)
    items[0] = {**items[0], key: value}
    (tmp_path / "data").mkdir()
    (tmp_path / "data/games.json").write_text(json.dumps(items))
    with pytest.raises(ModsError):
        load_catalog(tmp_path)


def test_duplicated_catalog_identity_and_series_are_rejected(tmp_path: Path) -> None:
    entries = load_catalog(ROOT)
    (tmp_path / "data").mkdir()
    entries[1] = copy.deepcopy(entries[0])
    target = tmp_path / "data/games.json"
    target.write_text(json.dumps(entries))
    with pytest.raises(ModsError):
        load_catalog(tmp_path)
    target.write_text(json.dumps([{**entry, "series": "same"} for entry in load_catalog(ROOT)]))
    with pytest.raises(ModsError):
        load_catalog(tmp_path)


@pytest.mark.parametrize(
    "text", ["broken", '"x"', "}", '"a" {', '"a" "b" "a" "c"', '"a" "b" garbage']
)
def test_malformed_vdf_is_rejected(tmp_path: Path, text: str) -> None:
    target = tmp_path / "manifest.acf"
    target.write_text(text)
    with pytest.raises(ValueError):
        read_vdf(target)


def test_vdf_comments_and_legacy_library_syntax(tmp_path: Path) -> None:
    steam_root = tmp_path / ".steam/root"
    sd = tmp_path / "SDCard"
    put(
        steam_root,
        "steamapps/libraryfolders.vdf",
        f'//Steam libraries\n"libraryfolders" {{ "1" "{sd}" }}'.encode(),
    )
    manifest(sd, "3489700", "SB")
    (sd / "steamapps/common/SB").mkdir(parents=True)
    assert SteamDiscovery(load_catalog(ROOT), tmp_path).resolve("stellarblade")["installed"]


def test_pending_download_and_mismatched_manifest_are_not_installed(tmp_path: Path) -> None:
    root = tmp_path / ".steam/root"
    (root / "steamapps/common/SB").mkdir(parents=True)
    manifest(root, "3489700", "SB", '"StateFlags" "1"')
    discovery = SteamDiscovery(load_catalog(ROOT), tmp_path)
    assert not discovery.resolve_optional("stellarblade")
    put(
        root, "steamapps/appmanifest_3489700.acf", b'"AppState" { "appid" "123" "installdir" "SB" }'
    )
    assert not discovery.resolve_optional("stellarblade")
    assert discovery.issues


def test_actual_process_appid_blocks_game_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / ".steam/root"
    manifest(root, "3489700", "SB")
    (root / "steamapps/common/SB").mkdir(parents=True)
    monkeypatch.setattr(steam, "_running_apps", lambda candidates: ({"3489700"}, set()))
    assert SteamDiscovery(load_catalog(ROOT), tmp_path).resolve("stellarblade")["running"]
    monkeypatch.setattr(steam, "_running_apps", lambda candidates: (set(), {"3489700"}))
    discovery = SteamDiscovery(load_catalog(ROOT), tmp_path)
    assert discovery.resolve("stellarblade")["running"]
    assert discovery.issues


def test_pak_option_wrappers_even_with_mods_anchors_are_not_all_installed(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    put(archive, "OptionA/SB/Content/Paks/~mods/a.pak")
    put(archive, "OptionB/SB/Content/Paks/~mods/b.pak")
    result = plan_files(game("stellarblade", tmp_path), archive)
    assert result["blocked_reason"] and not result["files"]


def test_existing_case_is_preserved_and_symlinked_destinations_rejected(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    (install / "codevein/content/paks").mkdir(parents=True)
    put(archive, "outfit.pak")
    selected = game("codevein", install)
    assert (
        plan_files(selected, archive)["files"][0]["target"]
        == "codevein/content/paks/~mods/outfit.pak"
    )
    (install / "codevein/content/paks/~mods").symlink_to(archive, target_is_directory=True)
    with pytest.raises(ModsError):
        plan_files(selected, archive)


def test_multiple_flat_paks_are_independent_and_have_warning(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    put(archive, "a.pak")
    put(archive, "b.pak")
    result = plan_files(game("stellarblade", tmp_path), archive)
    assert len(result["files"]) == 2 and len(result["warnings"]) == 2


def test_re4_single_pak_returns_renumber_metadata_only(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    put(install, "dinput8.dll")
    put(install, "re_chunk_000.pak")
    put(archive, "re_chunk_000.pak.patch_007.pak")
    result = plan_files(game("residentevil42023", install), archive)
    assert result["blocked_reason"] is None
    assert result["files"] == [
        {
            "source": "re_chunk_000.pak.patch_007.pak",
            "target": "re_chunk_000.pak.patch_007.pak",
            "kind": "re_pak",
        }
    ]
    assert not (install / "re_chunk_000.pak.patch_007.pak").exists()


@pytest.mark.parametrize(
    "layout",
    [
        "file.pak",
        "reframework/config.ini",
        "reframework/autorun",
        "reframework/plugins/readme.cfg",
        "natives/a",
        "run.exe",
    ],
)
def test_reframework_unknown_layouts_block(tmp_path: Path, layout: str) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    put(install, "dinput8.dll")
    put(archive, layout)
    result = plan_files(game("residentevil42023", install), archive)
    assert result["blocked_reason"] and not result["files"]


def test_reframework_plugin_and_duplicate_targets(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    put(install, "dinput8.dll")
    put(archive, "Mod/reframework/plugins/example.dll")
    selected = game("residentevil42023", install)
    assert plan_files(selected, archive)["blocked_reason"] is None
    put(archive, "Other/reframework/plugins/example.dll")
    assert plan_files(selected, archive)["blocked_reason"]


def test_legacy_re4_multiple_pak_variants_are_blocked(tmp_path: Path) -> None:
    install, archive = tmp_path / "install", tmp_path / "archive"
    put(install, "dinput8.dll")
    put(install, "re_chunk_000.pak")
    for number in ["001", "002"]:
        put(archive, f"re_chunk_000.pak.patch_{number}.pak")
    assert plan_files(game("residentevil42023", install), archive)["blocked_reason"]


def test_unrelated_protected_process_does_not_block_games(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    game_root = tmp_path / "game"
    put(game_root, "game.exe")
    proc = tmp_path / "proc"
    put(proc, "123/environ")
    put(proc, "123/cmdline", b"steamwebhelper\x00--sandbox\x00")
    put(proc, "123/comm", b"steamwebhelper\n")
    original_open = Path.open

    def guarded_open(path: Path, *args: object, **kwargs: object):
        if path == proc / "123/environ":
            raise PermissionError("protected unrelated process")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(steam, "_PROC_ROOT", proc)
    monkeypatch.setattr(steam.sys, "platform", "linux")
    monkeypatch.setattr(Path, "open", guarded_open)
    assert steam._running_apps({"1234": game_root}) == (set(), set())
    put(proc, "123/cmdline", (str(game_root / "game.exe") + "\x00").encode())
    assert steam._running_apps({"1234": game_root}) == (set(), {"1234"})


def test_linux_process_environment_detects_actual_game(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    put(tmp_path, "proc/123/environ", b"SteamAppId=1234\x00SteamGameId=0\x00")
    monkeypatch.setattr(steam, "_PROC_ROOT", tmp_path / "proc")
    monkeypatch.setattr(steam.sys, "platform", "linux")
    assert steam._running_apps({"1234": tmp_path}) == ({"1234"}, set())


def test_config_libraryfolders_fallback(tmp_path: Path) -> None:
    root = tmp_path / ".steam/root"
    sd = tmp_path / "SD library"
    put(
        root,
        "config/libraryfolders.vdf",
        f'"libraryfolders" {{ "1" {{ "path" "{sd}" }} }}'.encode(),
    )
    manifest(sd, "3489700", "StellarBlade")
    (sd / "steamapps/common/StellarBlade").mkdir(parents=True)
    assert SteamDiscovery(load_catalog(ROOT), tmp_path).resolve("stellarblade")["installed"]
