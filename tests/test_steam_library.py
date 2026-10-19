"""Installed games outside the reviewed adapter catalog remain safely manageable."""

from pathlib import Path

import pytest
from decky_mods.catalog import load_catalog
from decky_mods.errors import ModsError
from decky_mods.steam import SteamDiscovery

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = [
    ("4628710", "Proton 11.0"),
    ("3658110", "Proton 10.0"),
    ("1391110", "Steam Linux Runtime 2.0 (soldier)"),
    ("1628350", "Steam Linux Runtime 3.0 (sniper)"),
    ("1070560", "Steam Linux Runtime 1.0 (scout)"),
    ("4183110", "Steam Linux Runtime 4.0"),
    ("1493710", "Proton Experimental"),
    ("228980", "Steamworks Common Redistributables"),
    ("1161040", "Proton BattlEye Runtime"),
]


def installed(library: Path, app_id: str, name: str, flags: str = "4") -> Path:
    root = library / "steamapps/common" / app_id
    root.mkdir(parents=True, exist_ok=True)
    (library / f"steamapps/appmanifest_{app_id}.acf").write_text(
        f'"AppState" {{ "appid" "{app_id}" "name" "{name}" '
        f'"installdir" "{app_id}" "StateFlags" "{flags}" "buildid" "234" }}'
    )
    return root


@pytest.fixture
def discovery(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SteamDiscovery:
    monkeypatch.setattr("decky_mods.steam._running_apps", lambda candidates: (set(), set()))
    return SteamDiscovery(load_catalog(ROOT), tmp_path)


def test_actual_deck_library_contains_all_five_games_and_no_runtimes(discovery) -> None:
    library = discovery.home / ".local/share/Steam"
    expected = {
        "1623730": "Palworld",
        "418370": "Resident Evil 7",
        "2358720": "Black Myth: Wukong",
        "1245620": "ELDEN RING",
        "2399830": "ARK: Survival Ascended",
    }
    for app_id, name in [*expected.items(), *RUNTIMES]:
        installed(library, app_id, name)
    games = [game for game in discovery.discover() if game["installed"]]
    assert {game["app_id"] for game in games} == set(expected)
    catalog = {game["id"]: game for game in discovery.catalog}
    reviewed = {
        "1623730": "palworld",
        "418370": "residentevil7",
        "2358720": "blackmythwukong",
        "1245620": "eldenring",
    }
    for game in games:
        if game["app_id"] in reviewed:
            assert game["id"] == reviewed[game["app_id"]]
            assert game["id"] in catalog
            assert game["adapter"] == catalog[game["id"]]["adapter"]
        else:
            assert game["id"] == "steam-" + game["app_id"]
            assert game["name"] == expected[game["app_id"]]
            assert game["support"] == game["adapter"] == "catalog"
            assert game["nexus_domain"] == ""
            assert game["adapter_config"] == {}
            assert any("根目录" in value and "ZIP" in value for value in game["requirements"])
            assert game["sources"] == [f"https://store.steampowered.com/app/{game['app_id']}/"]
            assert game["build_id"] == "234"


def test_dynamic_sd_library_is_deduplicated_and_needs_no_top_level_exe(discovery, tmp_path) -> None:
    library = discovery.home / ".local/share/Steam"
    sd = tmp_path / "SD Card/SteamLibrary"
    game = installed(sd, "390000001", "Synthetic Unreal title")
    (game / "b1/Binaries/Win64").mkdir(parents=True)
    (game / "b1/Binaries/Win64/b1.exe").write_bytes(b"MZgame")
    config = library / "steamapps/libraryfolders.vdf"
    config.parent.mkdir(parents=True)
    config.write_text(
        f'"libraryfolders" {{ "0" {{ "path" "{library}" }} '
        f'"1" {{ "path" "{sd}" }} "2" {{ "path" "{sd}" }} }}'
    )
    alias = discovery.home / ".steam"
    alias.mkdir()
    (alias / "steam").symlink_to(library, target_is_directory=True)
    matches = [game for game in discovery.discover() if game["id"] == "steam-390000001"]
    assert len(matches) == 1
    assert discovery.resolve("steam-390000001")["path"] == str(game)


@pytest.mark.parametrize("flags", ["0", "1", "2", "512", "invalid"])
def test_partial_unknown_installs_never_become_deployment_roots(discovery, flags) -> None:
    installed(discovery.home / ".local/share/Steam", "390000001", "Synthetic game", flags)
    assert discovery.resolve_optional("steam-390000001") is None
    assert not any(game["id"] == "steam-390000001" for game in discovery.discover())


@pytest.mark.parametrize("flags", ["260", "516", "1028", "4100"])
def test_unknown_updating_installs_are_visible_but_cannot_deploy(discovery, flags) -> None:
    installed(discovery.home / ".local/share/Steam", "390000001", "Synthetic game", flags)
    game = next(game for game in discovery.discover() if game["id"] == "steam-390000001")
    assert game["installed"] and game["updating"]
    with pytest.raises(ModsError):
        discovery.resolve("steam-390000001")


@pytest.mark.parametrize("flags", ["6", "516", "550"])
def test_paused_or_pending_updates_remain_mod_locked_without_blocking_plugin_updates(
    discovery, flags
):
    installed(discovery.home / ".local/share/Steam", "2399830", "Synthetic game", flags)
    game = next(game for game in discovery.discover() if game["app_id"] == "2399830")
    assert game["updating"] is True
    assert game["update_active"] is False
    with pytest.raises(ModsError):
        discovery.resolve(game["id"])


@pytest.mark.parametrize("flags", ["260", "1028", "4100", "1048580", "16777220"])
def test_active_or_unknown_maintenance_still_blocks_plugin_update(discovery, flags):
    installed(discovery.home / ".local/share/Steam", "2399830", "Synthetic game", flags)
    game = next(game for game in discovery.discover() if game["app_id"] == "2399830")
    assert game["update_active"] is True


@pytest.mark.parametrize("app_id", ["0", "01", "4294967296", "9999999999", "-1", "text"])
def test_manifest_appids_must_be_canonical_uint32(discovery, app_id) -> None:
    installed(discovery.home / ".local/share/Steam", app_id, "Invalid app")
    assert not any(game["installed"] for game in discovery.discover())


def test_uint32_limit_and_legitimate_proton_title_are_discoverable(discovery) -> None:
    installed(discovery.home / ".local/share/Steam", "4294967295", "Proton Pulse")
    assert discovery.resolve("steam-4294967295")["name"] == "Proton Pulse"


@pytest.mark.parametrize(
    "contents",
    [
        '"AppState" { "appid" "390000002" "installdir" "390000001" }',
        '"AppState" { "appid" "390000001" "installdir" "../outside" }',
        '"AppState" { "appid" "390000001" "installdir" "/outside" }',
        '"AppState" { "appid" "390000001" "installdir" "nested/game" }',
        '"AppState" { "appid" "390000001" "installdir" "390000001" "name" { } }',
        '"AppState" { "appid" "390000001"',
    ],
)
def test_invalid_unknown_manifests_fail_closed(discovery, contents) -> None:
    library = discovery.home / ".local/share/Steam"
    installed(library, "390000001", "Synthetic game")
    (library / "steamapps/appmanifest_390000001.acf").write_text(contents)
    assert discovery.resolve_optional("steam-390000001") is None
    assert discovery.issues


@pytest.mark.parametrize("part", ["manifest", "game", "common", "steamapps"])
def test_unknown_manifest_and_internal_directory_links_are_rejected(
    discovery, tmp_path, part
) -> None:
    library = discovery.home / ".local/share/Steam"
    root = installed(library, "390000001", "Synthetic game")
    target = {
        "manifest": library / "steamapps/appmanifest_390000001.acf",
        "game": root,
        "common": root.parent,
        "steamapps": root.parent.parent,
    }[part]
    moved = tmp_path / ("outside-" + part)
    target.rename(moved)
    target.symlink_to(moved, target_is_directory=moved.is_dir())
    assert discovery.resolve_optional("steam-390000001") is None


@pytest.mark.parametrize("app_id,name", RUNTIMES)
def test_known_runtime_ids_are_not_misclassified_without_tool_names(
    discovery, app_id, name
) -> None:
    installed(discovery.home / ".local/share/Steam", app_id, "Missing descriptive name")
    assert not any(game["app_id"] == app_id for game in discovery.discover())


@pytest.mark.parametrize("name", [name for _, name in RUNTIMES] + ["Proton Hotfix"])
def test_new_runtime_versions_with_recognizable_names_are_excluded(discovery, name) -> None:
    installed(discovery.home / ".local/share/Steam", "4000000000", name)
    assert not any(game["app_id"] == "4000000000" for game in discovery.discover())


def test_running_process_detection_also_receives_discovered_games(discovery, monkeypatch) -> None:
    root = installed(discovery.home / ".local/share/Steam", "390000001", "Synthetic game")

    def running(candidates):
        assert candidates["390000001"] == root
        return {"390000001"}, set()

    monkeypatch.setattr("decky_mods.steam._running_apps", running)
    assert discovery.resolve("steam-390000001")["running"]


def test_scan_is_bounded_and_reports_truncation(discovery, monkeypatch) -> None:
    library = discovery.home / ".local/share/Steam"
    for app_id in ("390000001", "390000002", "2399830"):
        installed(library, app_id, "Game")
    monkeypatch.setattr("decky_mods.steam_library.MAX_MANIFESTS", 2)
    assert len([game for game in discovery.discover() if game["installed"]]) == 2
    assert discovery.issues


def test_duplicate_appid_across_libraries_has_one_stable_identity(discovery, tmp_path) -> None:
    library = discovery.home / ".local/share/Steam"
    sd = tmp_path / "SD/SteamLibrary"
    installed(library, "390000001", "Synthetic game")
    installed(sd, "390000001", "Synthetic game")
    (library / "steamapps/libraryfolders.vdf").write_text(
        f'"libraryfolders" {{ "1" {{ "path" "{sd}" }} }}'
    )
    assert len([game for game in discovery.discover() if game["id"] == "steam-390000001"]) == 1


def test_library_and_entry_limits_report_issues(discovery, tmp_path, monkeypatch) -> None:
    library = discovery.home / ".local/share/Steam"
    sd = tmp_path / "SD/SteamLibrary"
    installed(library, "390000001", "Synthetic game")
    installed(sd, "390000002", "Second synthetic game")
    (library / "steamapps/libraryfolders.vdf").write_text(
        f'"libraryfolders" {{ "1" {{ "path" "{sd}" }} }}'
    )
    monkeypatch.setattr("decky_mods.steam.MAX_LIBRARIES", 1)
    assert discovery.resolve_optional("steam-390000002") is None
    assert discovery.issues
    monkeypatch.setattr("decky_mods.steam_library.MAX_DIRECTORY_ENTRIES", 0)
    assert not any(game["id"] == "steam-390000001" for game in discovery.discover())
    assert any("上限" in issue for issue in discovery.issues)


@pytest.mark.parametrize("first_id", ["3489700", "390000000"])
def test_dynamic_manifest_alias_cannot_create_independent_mod_state(discovery, first_id) -> None:
    library = discovery.home / ".local/share/Steam"
    installed(library, first_id, "Existing game")
    installed(library, "390000001", "Alias")
    (library / "steamapps/appmanifest_390000001.acf").write_text(
        f'"AppState" {{ "appid" "390000001" "name" "Alias" '
        f'"installdir" "{first_id}" "StateFlags" "4" }}'
    )
    games = [game for game in discovery.discover() if game["installed"]]
    assert len(games) == 1
    assert games[0]["app_id"] == first_id
    assert discovery.issues


@pytest.mark.parametrize("layout", ["same-root", "nested-library"])
def test_two_catalog_games_cannot_own_the_same_or_overlapping_roots(discovery, layout):
    library = discovery.home / ".local/share/Steam"
    first = installed(library, "3489700", "First reviewed game")
    if layout == "same-root":
        installed(library, "2358720", "Second reviewed game")
        (library / "steamapps/appmanifest_2358720.acf").write_text(
            '"AppState" { "appid" "2358720" "name" "Second reviewed game" '
            '"installdir" "3489700" "StateFlags" "4" }'
        )
    else:
        nested = first / "NestedLibrary"
        installed(nested, "2358720", "Second reviewed game")
        (library / "steamapps/libraryfolders.vdf").write_text(
            f'"libraryfolders" {{ "1" {{ "path" "{nested}" }} }}'
        )
    games = [game for game in discovery.discover() if game["installed"]]
    assert len(games) == 1
    assert discovery.issues


def test_nested_declared_library_cannot_create_overlapping_game_roots(discovery) -> None:
    library = discovery.home / ".local/share/Steam"
    root = installed(library, "3489700", "Existing reviewed game")
    nested = root / "NestedLibrary"
    installed(nested, "390000001", "Nested title")
    (library / "steamapps/libraryfolders.vdf").write_text(
        f'"libraryfolders" {{ "1" {{ "path" "{nested}" }} }}'
    )
    assert len([game for game in discovery.discover() if game["installed"]]) == 1
    assert discovery.issues


def test_same_inode_game_roots_cannot_create_independent_mod_state(discovery, monkeypatch) -> None:
    library = discovery.home / ".local/share/Steam"
    first = installed(library, "390000002", "First game")
    second = installed(library, "390000001", "Second game")
    stat = Path.stat

    def shared_inode(path, *args, **kwargs):
        return stat(first if path == second else path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", shared_inode)
    assert len([game for game in discovery.discover() if game["installed"]]) == 1
    assert discovery.issues
