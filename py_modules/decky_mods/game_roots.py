"""Explicit manual game roots; automatic Steam discovery remains the default."""

import os
import stat
import threading
from pathlib import Path

from ._nexus_private import read_json, write_json
from .errors import ModsError
from .paths import private_directory
from .steam import _running_apps


class GameRoots:
    def __init__(self, directory: Path, discovery, home: Path):
        self.directory, self.discovery, self.home = directory, discovery, home.resolve()
        private_directory(directory)
        self.path = directory / "roots.json"
        self.lock = threading.RLock()
        saved = read_json(self.path) or {}
        if not isinstance(saved.get("roots", {}), dict):
            raise ModsError("手动游戏目录设置无效，请保留备份后检查设置")
        self.roots = saved.get("roots", {})

    def _validate(self, raw: str) -> Path:
        if not isinstance(raw, str) or len(raw) > 4096 or any(ord(c) < 32 for c in raw):
            raise ModsError("请选择有效的游戏文件夹")
        path = Path(raw)
        if not path.is_absolute() or ".." in path.parts:
            raise ModsError("游戏目录必须为完整路径")
        try:
            if any(parent.is_symlink() for parent in [path, *path.parents]):
                raise ModsError("手动游戏目录不能包含符号链接，请选择真实文件夹")
            path = path.resolve(strict=True)
            libraries = (
                self.discovery._libraries()[0] if hasattr(self.discovery, "_libraries") else []
            )
            common_roots = [library / "steamapps/common" for library in libraries]
            in_library = any(path.parent == common for common in common_roots)
            in_home = path.is_relative_to(self.home) and path != self.home
            relative = path.relative_to(self.home) if in_home else None
            in_media = path.is_relative_to("/run/media") and len(path.parts) >= 6
            if not in_library and not (
                (in_home and relative and not any(part.startswith(".") for part in relative.parts))
                or in_media
            ):
                raise ModsError("请选择个人游戏文件夹或 Steam 游戏库中的游戏目录")
            if not in_library and any(
                part.casefold()
                in {
                    "pfx",
                    "drive_c",
                    "userdata",
                    "compatdata",
                    "homebrew",
                    "plugins",
                    "settings",
                    "steamapps",
                }
                for part in path.parts
            ):
                raise ModsError("不能将容器、Steam 资料或插件目录作为游戏根目录")
            if path.name.casefold() in {
                "home",
                "downloads",
                "documents",
                "desktop",
                "games",
                "steam",
                "steamapps",
                "common",
                "userdata",
                "compatdata",
                "pfx",
                "homebrew",
                "plugins",
                "settings",
            }:
                raise ModsError("请选择具体游戏文件夹，不能选择系统、资料或游戏库总目录")
            info = path.stat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                raise ModsError("游戏文件夹必须属于当前用户")
            executable = False
            for index, entry in enumerate(path.iterdir()):
                if index > 4096:
                    raise ModsError("目录内容过多，请选择具体游戏文件夹")
                if entry.suffix.casefold() != ".exe" or entry.is_symlink():
                    continue
                descriptor = os.open(entry, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                with os.fdopen(descriptor, "rb") as stream:
                    if stat.S_ISREG(os.fstat(stream.fileno()).st_mode) and stream.read(2) == b"MZ":
                        executable = True
                        break
            if not executable:
                raise ModsError("此目录未找到 Windows 游戏 EXE，请选择包含游戏启动文件的根目录")
            return path
        except OSError:
            raise ModsError("游戏目录不可用，请检查存储卡和文件权限") from None

    def configure(self, game_id: str, mode: str, raw: str) -> None:
        with self.lock:
            game = next((game for game in self.discover() if game["id"] == game_id), None)
            if not game or game["adapter"] != "catalog":
                raise ModsError("仅未适配游戏可以手动设置根目录")
            if game.get("running") or game.get("updating"):
                raise ModsError("请先退出游戏并等待 Steam 更新结束")
            if mode not in {"auto", "manual"}:
                raise ModsError("目录定位模式无效")
            selected = self._validate(raw) if mode == "manual" else None
            if selected:
                self._exclusive(game_id, selected, self.discovery.discover())
                app_id = game.get("app_id") or game["steam_app_ids"][0]
                running, uncertain = _running_apps({app_id: selected}, match_paths=True)
                if app_id in running or app_id in uncertain:
                    raise ModsError("请先退出游戏，再选择游戏目录")
            roots = {key: value for key, value in self.roots.items() if key != game_id}
            if selected:
                roots = {**roots, game_id: str(selected)}
            write_json(self.path, {"roots": roots})
            self.roots = roots

    def _exclusive(self, game_id: str, selected: Path, games: list[dict]) -> None:
        identity = selected.stat()
        others = [raw for ident, raw in self.roots.items() if ident != game_id]
        others += [game["path"] for game in games if game["id"] != game_id and game.get("path")]
        for raw in others:
            other = Path(raw)
            try:
                info = other.stat()
            except FileNotFoundError:
                continue
            except OSError:
                raise ModsError("无法检查其他游戏目录，请检查存储卡和文件权限") from None
            if (
                selected.is_relative_to(other)
                or other.is_relative_to(selected)
                or (info.st_dev, info.st_ino) == (identity.st_dev, identity.st_ino)
            ):
                raise ModsError("所选游戏目录与另一个游戏相同或重叠")

    def discover(self) -> list[dict]:
        with self.lock:
            roots = dict(self.roots)
        result = []
        games = self.discovery.discover()
        for game in games:
            raw = roots.get(game["id"])
            if raw is None:
                result.append({**game, "manual_root": False, "root_error": None})
                continue
            try:
                if game["adapter"] != "catalog":
                    raise ModsError("游戏适配方式已更新，请保留原部署记录后检查目录")
                root = self._validate(raw)
                self._exclusive(game["id"], root, games)
                result.append(
                    {
                        **game,
                        "path": str(root),
                        "installed": True,
                        "app_id": game.get("app_id") or game["steam_app_ids"][0],
                        "manual_root": True,
                        "root_error": None,
                    }
                )
            except ModsError as error:
                result.append(
                    {
                        **game,
                        "path": None,
                        "installed": False,
                        "manual_root": True,
                        "root_error": str(error),
                    }
                )
        candidates = {
            game["app_id"]: Path(game["path"])
            for game in result
            if game["installed"] and game.get("manual_root")
        }
        running, uncertain = (
            _running_apps(candidates, match_paths=True) if candidates else (set(), set())
        )
        return [
            {
                **game,
                "running": game.get("running", False)
                or game["app_id"] in running
                or game["app_id"] in uncertain,
            }
            for game in result
        ]

    def resolve(self, game_id: str) -> dict:
        game = next((game for game in self.discover() if game["id"] == game_id), None)
        if not game or not game["installed"] or game.get("updating"):
            raise ModsError("未找到可用游戏根目录，请自动定位或手动选择游戏文件夹")
        return game
