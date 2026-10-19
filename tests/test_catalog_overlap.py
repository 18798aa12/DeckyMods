"""New catalog coverage cannot give overlapping games independent deployment state."""

from decky_mods.catalog import load_catalog
from decky_mods.steam import SteamDiscovery

from tests.test_steam_library import ROOT, installed


def test_two_catalog_manifests_sharing_a_root_have_one_installed_identity(tmp_path, monkeypatch):
    library = tmp_path / ".local/share/Steam"
    installed(library, "3489700", "Stellar Blade")
    installed(library, "2358720", "Black Myth")
    manifest = library / "steamapps/appmanifest_2358720.acf"
    manifest.write_text(
        manifest.read_text().replace('"installdir" "2358720"', '"installdir" "3489700"')
    )
    monkeypatch.setattr("decky_mods.steam._running_apps", lambda candidates: (set(), set()))
    discovery = SteamDiscovery(load_catalog(ROOT), tmp_path)
    games = [g for g in discovery.discover() if g["installed"]]
    assert len(games) == 1
    assert discovery.issues
