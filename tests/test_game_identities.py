"""Catalog expansion preserves the identity that owns local MOD records."""

import json
import sqlite3
import zipfile

import pytest
from decky_mods.database import Database
from decky_mods.errors import ModsError
from decky_mods.service import Service
from decky_mods.steam import SteamDiscovery

from tests.test_service import Handler, Nexus, wait_job
from tests.test_steam_library import ROOT, installed

APP = "2358720"
LEGACY = "steam-" + APP


def reviewed(*apps):
    return {
        "id": "reviewed-title",
        "name": "Reviewed title",
        "series": "reviewed",
        "series_name": "Reviewed",
        "steam_app_ids": list(apps or [APP]),
        "adapter": "reframework",
        "adapter_config": {"native_config": "config.ini"},
        "nexus_domain": "reviewed",
        "support": "automatic",
        "requirements": [],
        "sources": [],
        "validation": "Synthetic reviewed mapping",
    }


@pytest.fixture
def library(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / "Downloads").mkdir(parents=True)
    steam = home / ".local/share/Steam"
    root = installed(steam, APP, "Original title")
    (root / "Game.exe").write_bytes(b"MZgame")
    monkeypatch.setattr("decky_mods.steam._running_apps", lambda *a, **k: (set(), set()))
    monkeypatch.setattr("decky_mods.game_roots._running_apps", lambda *a, **k: (set(), set()))
    services = []

    def start(catalog=()):
        instance = Service(
            ROOT,
            tmp_path / "state",
            home=home,
            discovery=SteamDiscovery(list(catalog), home),
            nexus=Nexus(),
            handler=Handler(),
        )
        services.append(instance)
        return instance

    yield start, home, steam, root
    for instance in services:
        instance.close()


def archive(home):
    path = home / "Downloads/test.zip"
    with zipfile.ZipFile(path, "w") as output:
        output.writestr("settings.ini", b"modified")
    return path


def ready(service, home):
    job = service.import_archive(LEGACY, str(archive(home)), "Local MOD", "game_root")
    current = wait_job(service, job["id"])
    assert current["phase"] == "ready", current
    return current


def assert_legacy(service):
    games = service.list_games()
    assert [game["id"] for game in games] == [LEGACY]
    game = games[0]
    assert game["adapter"] == game["support"] == "catalog"
    assert game["nexus_domain"] == "" and game["adapter_config"] == {}
    assert game["steam_app_ids"] == [APP]
    return game


def test_installed_mod_restart_with_new_mapping_preserves_restore_and_identity(library):
    start, home, _, root = library
    (root / "settings.ini").write_bytes(b"original")
    original = start()
    job = ready(original, home)
    original.install_plan(job["plan_id"], True)
    assert wait_job(original, job["id"])["phase"] == "complete"
    mod = original.get_game(LEGACY)["mods"][0]
    original.close()
    current = start([reviewed()])
    ledger = current.directory / "game-identities/identities.json"
    before = (root / "settings.ini").read_bytes()
    (current.launch_options.directory / f"{APP}.json").write_bytes(b"existing private journal")
    journals = {path: path.read_bytes() for path in current.launch_options.directory.iterdir()}
    assert assert_legacy(current)["path"] == str(root)
    assert assert_legacy(current)["name"] == "Original title"
    assert current.get_game(LEGACY)["mods"] == [mod]
    stamp = ledger.stat().st_mtime_ns
    current.list_games()
    assert ledger.stat().st_mtime_ns == stamp
    assert (root / "settings.ini").read_bytes() == before
    observed = {path: path.read_bytes() for path in current.launch_options.directory.iterdir()}
    assert observed == journals
    current.set_mod_enabled(LEGACY, mod["id"], False)
    assert (root / "settings.ini").read_bytes() == b"original"
    current.set_mod_enabled(LEGACY, mod["id"], True)
    current.uninstall_mod(LEGACY, mod["id"])
    assert (root / "settings.ini").read_bytes() == b"original"
    # Even after task pruning/uninstall, persisted ownership cannot silently upgrade adapters.
    with current.engine.db.connection() as connection:
        connection.execute("DELETE FROM games")
        connection.execute("DELETE FROM plans")
    with current.jobs.lock:
        current.jobs.rows = {}
        current.jobs._save()
    current.close()
    assert_legacy(start([reviewed()]))


def test_ready_job_and_plan_survive_catalog_expansion_and_install(library):
    start, home, _, root = library
    original = start()
    job = ready(original, home)
    original.close()
    current = start([reviewed()])
    assert_legacy(current)
    assert current.get_plan(job["plan_id"])["game_id"] == LEGACY
    assert current.get_jobs()[0]["id"] == job["id"]
    current.install_plan(job["plan_id"], False)
    assert wait_job(current, job["id"])["phase"] == "complete"
    assert (root / "settings.ini").read_bytes() == b"modified"


@pytest.mark.parametrize("reference", ["game", "pending", "plan", "job", "manual"])
def test_preexisting_reference_infers_ownership_without_prior_ledger(library, reference):
    start, home, _, root = library
    original = start()
    if reference == "game":
        with original.engine.db.connection() as connection:
            connection.execute("INSERT INTO games VALUES (?, ?)", (LEGACY, '{"mods": []}'))
    elif reference == "pending":
        original.engine.db.begin({"id": "pending", "game_id": LEGACY})
    elif reference == "plan":
        original.engine.db.save_plan({"id": "preview", "game_id": LEGACY})
    elif reference == "job":
        original.jobs.create(LEGACY, "Local task", "ready")
    else:
        original.set_game_root(LEGACY, "manual", str(root))
    ledger = original.directory / "game-identities/identities.json"
    ledger.unlink(missing_ok=True)
    original.close()
    current = start([reviewed()])
    game = assert_legacy(current)
    assert game["path"] == str(root)
    assert game["manual_root"] is (reference == "manual")
    assert json.loads(ledger.read_text())["games"][0]["id"] == LEGACY


def test_missing_steam_retains_unavailable_row_and_never_trusts_saved_deployment_path(library):
    start, _, steam, root = library
    original = start()
    with original.engine.db.connection() as connection:
        state = {"mods": [], "fingerprint": {"path": str(root)}}
        connection.execute("INSERT INTO games VALUES (?, ?)", (LEGACY, json.dumps(state)))
    original.close()
    manifest = steam / f"steamapps/appmanifest_{APP}.acf"
    contents = manifest.read_text()
    manifest.unlink()
    current = start([reviewed()])
    missing = assert_legacy(current)
    assert not missing["installed"] and missing["path"] is None
    assert current.get_game(LEGACY)["mods"] == []
    with pytest.raises(ModsError):
        current.roots.resolve(LEGACY)
    manifest.write_text(contents)
    assert assert_legacy(current)["path"] == str(root)


def test_saved_manual_root_remains_authoritative_without_auto_fallback(library):
    start, home, _, _ = library
    original = start()
    manual = home / "Games/Manual title"
    manual.mkdir(parents=True)
    executable = manual / "Manual.exe"
    executable.write_bytes(b"MZgame")
    original.set_game_root(LEGACY, "manual", str(manual))
    original.close()
    current = start([reviewed()])
    assert assert_legacy(current)["path"] == str(manual)
    executable.unlink()
    missing = assert_legacy(current)
    assert missing["manual_root"] and missing["root_error"]
    assert not missing["installed"] and missing["path"] is None


def test_both_preexisting_owners_fail_closed_without_mutating_game(library):
    start, _, _, root = library
    original = start()
    for game_id in [LEGACY, "reviewed-title"]:
        original.engine.db.save_plan({"id": game_id, "game_id": game_id})
    original.close()
    current = start([reviewed()])
    before = (root / "Game.exe").read_bytes()
    with pytest.raises(ModsError, match="身份|记录|归属"):
        current.list_games()
    assert (root / "Game.exe").read_bytes() == before


def test_multi_app_mapping_never_borrows_another_variant_root(library):
    start, _, steam, root = library
    other = installed(steam, "1245620", "Another variant")
    original = start()
    original.jobs.create(LEGACY, "Local task", "ready")
    original.close()
    current = start([reviewed("1245620", APP)])
    assert assert_legacy(current)["path"] == str(root)
    (steam / f"steamapps/appmanifest_{APP}.acf").unlink()
    missing = assert_legacy(current)
    assert missing["path"] is None and not missing["installed"]
    assert str(other) != str(root)


@pytest.mark.parametrize(
    "corrupt",
    [
        {},
        {"version": 1, "games": [{"id": LEGACY, "app_id": APP, "name": "Title", "path": "/tmp"}]},
        {"version": 1, "games": [{"id": LEGACY, "app_id": "01", "name": "Title"}]},
        {"version": 1, "games": [{"id": LEGACY, "app_id": APP, "name": "Bad\nTitle"}]},
        {"version": 1, "games": [{"id": LEGACY, "app_id": APP, "name": " " * 501 + "Title"}]},
        {"version": True, "games": []},
        {"version": 1, "games": [{"id": LEGACY, "app_id": APP, "name": "Title"}] * 2},
    ],
)
def test_corrupt_identity_ledger_fails_closed(library, corrupt):
    start, _, _, _ = library
    original = start()
    directory = original.directory / "game-identities"
    directory.mkdir(exist_ok=True)
    (directory / "identities.json").write_text(json.dumps(corrupt))
    original.close()
    with pytest.raises(ModsError):
        start([reviewed()])


def test_unreferenced_discovered_game_may_use_new_reviewed_mapping(library):
    start, _, _, _ = library
    original = start()
    assert original.get_game(LEGACY)["game"]["adapter"] == "catalog"
    original.close()
    games = start([reviewed()]).list_games()
    assert [game["id"] for game in games] == ["reviewed-title"]


def test_pinned_manifest_alias_cannot_create_a_second_writer(library):
    start, _, steam, root = library
    original = start()
    original.jobs.create(LEGACY, "Local task", "ready")
    original.close()
    installed(steam, "1245620", "Conflicting title")
    (steam / "steamapps/appmanifest_1245620.acf").write_text(
        f'"AppState" {{ "appid" "1245620" "installdir" "{APP}" "StateFlags" "4" }}'
    )
    current = start([reviewed("1245620")])
    with pytest.raises(ModsError, match="身份|归属"):
        current.list_games()
    assert (root / "Game.exe").read_bytes() == b"MZgame"


def test_missing_installation_path_remains_unavailable_until_fresh_reconnect(library):
    start, _, _, root = library
    original = start()
    original.jobs.create(LEGACY, "Local task", "ready")
    original.close()
    moved = root.with_name("unavailable")
    root.rename(moved)
    current = start([reviewed()])
    assert not assert_legacy(current)["installed"]
    moved.rename(root)
    assert assert_legacy(current)["path"] == str(root)


def test_interrupted_transaction_recovers_under_original_identity_after_catalog_change(library):
    start, home, _, root = library
    (root / "settings.ini").write_bytes(b"original")
    original = start()
    job = ready(original, home)

    def power_loss(index, name):
        raise KeyboardInterrupt("synthetic power loss")

    original.engine.fault = power_loss
    with pytest.raises(KeyboardInterrupt):
        original.engine.install(original.roots.resolve(LEGACY), job["plan_id"], True)
    assert original.engine.db.pending(LEGACY)
    assert (root / "settings.ini").read_bytes() == b"modified"
    (original.directory / "game-identities/identities.json").unlink()
    original.close()
    current = start([reviewed()])
    current.recover_all()
    assert not current.engine.db.pending(LEGACY)
    assert (root / "settings.ini").read_bytes() == b"original"
    assert_legacy(current)


class WithoutSQLiteJSON:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, values=()):
        if "json_extract" in query:
            raise sqlite3.OperationalError("no such function: json_extract")
        return self.connection.execute(query, values)


def test_optional_sqlite_json_fallback_reads_large_valid_plan(library):
    start, _, _, _ = library
    instance = start()
    instance.engine.db.save_plan({"id": "large", "game_id": LEGACY, "mod": "x" * (3 * 1024**2)})
    with instance.engine.db.connection() as connection:
        legacy = Database._plan_game_ids(WithoutSQLiteJSON(connection), 4096)
        native = Database._plan_game_ids(connection, 4096)
    assert legacy == native == [LEGACY]
    assert instance.engine.db.referenced_game_ids() == {LEGACY}


@pytest.mark.parametrize("native", [True, False])
def test_plan_reference_count_is_bounded_and_malformed_plans_fail_closed(library, native):
    start, _, _, _ = library
    instance = start()
    for index in range(2):
        instance.engine.db.save_plan({"id": str(index), "game_id": LEGACY})
    with instance.engine.db.connection() as connection:
        source = connection if native else WithoutSQLiteJSON(connection)
        with pytest.raises(ModsError, match="记录|状态库"):
            Database._plan_game_ids(source, 1)
        connection.execute("UPDATE plans SET data='not json'")
        with pytest.raises((ModsError, sqlite3.DatabaseError)):
            Database._plan_game_ids(source, 4096)


def test_reference_overflow_does_not_silently_drop_owners(library, monkeypatch):
    start, _, _, _ = library
    instance = start()
    instance.jobs.create(LEGACY, "Local task", "ready")
    instance.jobs.create("steam-1245620", "Other local task", "ready")
    monkeypatch.setattr("decky_mods.game_identities.MAX_IDENTITIES", 1)
    with pytest.raises(ModsError, match="身份|归属"):
        instance.list_games()
