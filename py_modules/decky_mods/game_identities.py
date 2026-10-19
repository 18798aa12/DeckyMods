"""Keep durable discovered-game owners stable when the reviewed catalog expands."""

import json
import re
import threading
from pathlib import Path

from ._nexus_private import read_json
from .errors import ModsError
from .paths import atomic_write, private_directory
from .steam_library import InstallationRoots, discovered_entry, valid_app_id

MAX_IDENTITIES = 4096
MAX_LEDGER_BYTES = 16 * 1024 * 1024
_IDENT = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
_ERROR = "游戏身份归属记录无效或冲突，请保留私有设置和 MOD 备份后检查记录"
_LIVE_FIELDS = ("path", "app_id", "build_id", "running", "updating")


def _valid_name(value: object) -> bool:
    return (
        isinstance(value, str)
        and 1 <= len(value) <= 500
        and bool(value.strip())
        and not any(
            ord(char) < 32 or ord(char) == 127 or 0xD800 <= ord(char) <= 0xDFFF for char in value
        )
    )


class GameIdentities:
    """An ownership overlay, applied before manual-root validation and exclusivity."""

    def __init__(self, directory: Path, discovery, database, jobs, roots_path: Path):
        private_directory(directory)
        self.path = directory / "identities.json"
        self.discovery, self.database, self.jobs = discovery, database, jobs
        self.roots_path = roots_path
        self.lock = threading.RLock()
        saved = self._read(self.path, MAX_LEDGER_BYTES)
        self.identities = self._validate(saved) if saved is not None else {}

    @staticmethod
    def _read(path: Path, limit: int = 16384) -> dict | None:
        try:
            return read_json(path, limit=limit)
        except RecursionError:
            raise ModsError(_ERROR) from None

    @staticmethod
    def _validate(saved: dict) -> dict[str, dict]:
        if (
            set(saved) != {"version", "games"}
            or type(saved["version"]) is not int
            or saved["version"] != 1
            or not isinstance(saved["games"], list)
            or len(saved["games"]) > MAX_IDENTITIES
        ):
            raise ModsError(_ERROR)
        result = {}
        for row in saved["games"]:
            if (
                not isinstance(row, dict)
                or set(row) != {"id", "app_id", "name"}
                or not valid_app_id(row["app_id"])
                or row["id"] != "steam-" + row["app_id"]
                or row["id"] in result
                or not _valid_name(row["name"])
            ):
                raise ModsError(_ERROR)
            result = {**result, row["id"]: dict(row)}
        return result

    def _libraries(self):
        return self.discovery._libraries() if hasattr(self.discovery, "_libraries") else ([], [])

    def _references(self) -> set[str]:
        references = self.database.referenced_game_ids(limit=MAX_IDENTITIES)
        saved = self._read(self.roots_path) or {}
        roots = saved.get("roots", {})
        if not isinstance(roots, dict):
            raise ModsError(_ERROR)
        identifiers = [*references, *roots, *(job["game_id"] for job in self.jobs.list())]
        if any(
            not isinstance(ident, str)
            or not _IDENT.fullmatch(ident)
            or ident.startswith("steam-")
            and not valid_app_id(ident[6:])
            for ident in identifiers
        ):
            raise ModsError(_ERROR)
        references = set(identifiers)
        if len(references) > MAX_IDENTITIES:
            raise ModsError(_ERROR)
        return references

    def _retain(self, references: set[str], games: list[dict]) -> dict[str, dict]:
        identities = dict(self.identities)
        for ident in sorted(references):
            if ident in identities or not ident.startswith("steam-"):
                continue
            app_id = ident[6:]
            live = next((game for game in games if game.get("app_id") == app_id), {})
            name = live.get("name")
            identities = {
                **identities,
                ident: {
                    "id": ident,
                    "app_id": app_id,
                    "name": name if _valid_name(name) else f"Steam 游戏 {app_id}",
                },
            }
        if len(identities) > MAX_IDENTITIES:
            raise ModsError(_ERROR)
        return identities

    def _save(self, identities: dict[str, dict]) -> None:
        if identities == self.identities:
            return
        payload = json.dumps(
            {"version": 1, "games": list(identities.values())}, ensure_ascii=False
        ).encode("utf-8")
        if len(payload) > MAX_LEDGER_BYTES:
            raise ModsError(_ERROR)
        try:
            atomic_write(self.path, payload)
        except OSError:
            raise ModsError("无法安全保存游戏身份归属，请检查私有设置目录") from None
        self.identities = identities

    def _legacy_game(self, owner: dict, games: list[dict]) -> dict:
        app_id = owner["app_id"]
        live = next(
            (game for game in games if game.get("app_id") == app_id and game.get("installed")),
            None,
        )
        if live is None and hasattr(self.discovery, "discover_app"):
            live = self.discovery.discover_app(app_id)
        base = {
            **discovered_entry(app_id, owner["name"]),
            "installed": False,
            "path": None,
            "app_id": None,
            "build_id": None,
            "running": False,
            "updating": False,
        }
        if live is not None and live.get("app_id") == app_id and live.get("path"):
            return {**base, **{key: live.get(key) for key in _LIVE_FIELDS}, "installed": True}
        return base

    def discover(self) -> list[dict]:
        # Never hold the deployment lock here: callers may already hold the jobs lock.
        with self.lock:
            games = self.discovery.discover()
            references = self._references()
            identities = self._retain(references, games)
            owned = {row["app_id"] for row in identities.values()}
            result = []
            for game in games:
                overlaps = owned.intersection(game.get("steam_app_ids", []))
                if game["id"] in identities:
                    continue
                if overlaps:
                    if game["id"] in references:
                        raise ModsError(_ERROR)
                    continue
                result.append(game)
            result += [self._legacy_game(owner, games) for owner in identities.values()]
            # A new catalog alias must never create a second writer over an owned tree.
            if identities:
                roots = InstallationRoots()
                try:
                    for game in result:
                        if game.get("installed") and not roots.register(
                            Path(game["path"]), exclusive=True
                        ):
                            raise ModsError(_ERROR)
                except OSError:
                    raise ModsError("游戏目录已变化，请刷新游戏库后重试") from None
            self._save(identities)
            return result
