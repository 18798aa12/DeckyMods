import pytest
from decky_mods.errors import ModsError
from decky_mods.game_roots import GameRoots


class Discovery:
    def __init__(self, game):
        self.game = game

    def discover(self):
        return [dict(self.game)]


@pytest.fixture
def roots(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    game = {
        "id": "demo",
        "adapter": "catalog",
        "installed": False,
        "path": None,
        "app_id": None,
        "steam_app_ids": ["10"],
        "running": False,
        "updating": False,
    }
    discovery = Discovery(game)
    return GameRoots(tmp_path / "roots", discovery, home), discovery, home


def game_directory(home):
    root = home / "Games/Demo"
    root.mkdir(parents=True)
    (root / "Demo.exe").write_bytes(b"MZ" + b"\0" * 62)
    return root


def test_manual_selection_survives_reload_and_auto_clears_it(roots):
    resolver, discovery, home = roots
    root = game_directory(home)
    resolver.configure("demo", "manual", str(root))
    assert resolver.resolve("demo")["path"] == str(root)
    assert resolver.resolve("demo")["manual_root"]
    assert GameRoots(resolver.directory, discovery, home).resolve("demo")["path"] == str(root)
    resolver.configure("demo", "auto", "")
    assert not resolver.discover()[0]["installed"]


@pytest.mark.parametrize("relative", ["", ".local/share/private", "Downloads"])
def test_manual_selection_rejects_home_hidden_and_non_game_folders(roots, relative):
    resolver, _, home = roots
    path = home / relative
    path.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ModsError):
        resolver.configure("demo", "manual", str(path))


def test_manual_selection_rejects_symlink_escape_and_other_game(roots, tmp_path):
    resolver, discovery, home = roots
    root = game_directory(home)
    link = home / "shortcut"
    link.symlink_to(root, target_is_directory=True)
    with pytest.raises(ModsError):
        resolver.configure("demo", "manual", str(link))
    discovery.game = {**discovery.game, "adapter": "reframework"}
    with pytest.raises(ModsError):
        resolver.configure("demo", "manual", str(root))


def test_removed_manual_disk_never_falls_back_to_another_location(roots):
    resolver, discovery, home = roots
    root = game_directory(home)
    resolver.configure("demo", "manual", str(root))
    (root / "Demo.exe").unlink()
    current = resolver.discover()[0]
    assert not current["installed"] and current["manual_root"] and current["root_error"]
    with pytest.raises(ModsError):
        resolver.resolve("demo")


def test_manual_root_rejects_nested_proton_container(roots):
    resolver, _, home = roots
    root = home / "Games/pfx/drive_c/Game"
    root.mkdir(parents=True)
    (root / "game.exe").write_bytes(b"MZ")
    with pytest.raises(ModsError, match="容器"):
        resolver.configure("demo", "manual", str(root))


def test_two_games_cannot_share_one_manual_root(roots):
    resolver, discovery, home = roots
    root = game_directory(home)
    resolver.configure("demo", "manual", str(root))
    discovery.game = {**discovery.game, "id": "second"}
    with pytest.raises(ModsError, match="另一个游戏"):
        resolver.configure("second", "manual", str(root))


@pytest.mark.parametrize(
    "environ", [b"HOME=/tmp", b"SteamAppId=999999999999999", b"SteamAppId=999"]
)
def test_manual_running_game_without_catalog_appid_blocks_changes(
    roots, tmp_path, monkeypatch, environ
):
    import decky_mods.steam as steam

    resolver, _, home = roots
    root = game_directory(home)
    resolver.configure("demo", "manual", str(root))
    proc = tmp_path / "proc/123"
    proc.mkdir(parents=True)
    (proc / "environ").write_bytes(environ)
    (proc / "cmdline").write_bytes(str(root / "Demo.exe").encode() + b"\0")
    (proc / "cwd").symlink_to(root, target_is_directory=True)
    monkeypatch.setattr(steam, "_PROC_ROOT", proc.parent)
    monkeypatch.setattr(steam.sys, "platform", "linux")
    assert resolver.resolve("demo")["running"]
    with pytest.raises(ModsError, match="退出游戏"):
        resolver.configure("demo", "auto", "")


def test_manual_game_roots_must_not_overlap(roots):
    resolver, discovery, home = roots
    root = game_directory(home)
    resolver.configure("demo", "manual", str(root))
    nested = root / "Nested"
    nested.mkdir()
    (nested / "nested.exe").write_bytes(b"MZ")
    discovery.game = {**discovery.game, "id": "second"}
    with pytest.raises(ModsError, match="另一个游戏"):
        resolver.configure("second", "manual", str(nested))


def test_unrelated_running_game_does_not_block_root_selection(roots, monkeypatch):
    import decky_mods.game_roots as module

    resolver, _, home = roots
    root = game_directory(home)
    monkeypatch.setattr(module, "_running_apps", lambda *args, **kwargs: ({"999"}, set()))
    resolver.configure("demo", "manual", str(root))
    assert not resolver.resolve("demo")["running"]
