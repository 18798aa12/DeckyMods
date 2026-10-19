"""A partially updated Steam installation cannot safely accept MOD deployment."""

from pathlib import Path

import pytest
from decky_mods.catalog import load_catalog
from decky_mods.errors import ModsError
from decky_mods.steam import SteamDiscovery

ROOT = Path(__file__).resolve().parents[1]


def discovery(tmp_path, flags):
    steam = tmp_path / ".local/share/Steam"
    game = steam / "steamapps/common/StellarBlade"
    game.mkdir(parents=True)
    manifest = steam / "steamapps/appmanifest_3489700.acf"
    manifest.write_text(
        '"AppState" { "appid" "3489700" "installdir" "StellarBlade" '
        f'"buildid" "123" "StateFlags" "{flags}" }}'
    )
    return SteamDiscovery(load_catalog(ROOT), tmp_path), game


@pytest.mark.parametrize("extra_flags", [256, 512, 1024, 4096])
def test_installed_bit_does_not_allow_deployment_while_steam_is_updating(tmp_path, extra_flags):
    steam, game_directory = discovery(tmp_path, 4 | extra_flags)
    visible = next(item for item in steam.discover() if item["id"] == "stellarblade")
    assert visible["installed"]
    assert visible["updating"]
    assert steam.resolve_optional("stellarblade") is None
    with pytest.raises(ModsError, match="安装|更新|验证"):
        steam.resolve("stellarblade")
    assert game_directory.is_dir()
    assert list(game_directory.iterdir()) == []


def test_only_fully_installed_state_remains_available(tmp_path):
    steam, game_directory = discovery(tmp_path, 4)
    selected = steam.resolve("stellarblade")
    assert selected["installed"]
    assert selected["path"] == str(game_directory)
    assert selected["build_id"] == "123"
