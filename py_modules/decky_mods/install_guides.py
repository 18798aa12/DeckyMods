"""Read-only researched routes and explicit, separately reviewed deployment permissions."""

import copy
import json
import re
import threading
from pathlib import Path
from urllib.parse import urlsplit

from .errors import ModsError
from .profile_install import HANDLERS

_IDENT = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
# Game IDs remain durable: matching uses current verified Steam evidence as well.
_PROFILE_APPS = {
    "smapi": {"413150"},
    "cyberpunk_archive": {"1091500"},
    "witcher3_mods": {"292030"},
    "bethesda_data": {
        "72850",
        "489830",
        "611670",
        "377160",
        "22370",
        "22300",
        "22380",
        "22330",
    },
    "bepinex_plugins": {
        "892970",
        "1966720",
        "632360",
        "2881650",
        "3241660",
        "1366540",
        "264710",
        "848450",
    },
}
_PROFILE_INFO = {
    "smapi": (
        "SMAPI 单个 MOD / Content Pack",
        "Mods/<manifest 所在目录>",
        "必须已有匹配游戏版本的 SMAPI；安装预览列出清单声明的框架、依赖与最低版本，请先确认。",
    ),
    "cyberpunk_archive": (
        "Cyberpunk archive 资源",
        "archive/pc/mod",
        "仅 .archive 和配套 .archive.xl；XL 需要作者指定的 ArchiveXL。"
        "REDmod、CET、RED4ext 另用专用工具。",
    ),
    "witcher3_mods": (
        "巫师 3 标准 Mods 资源",
        "Mods/mod*/content",
        "请先确认 Classic 1.32 / Next-Gen 4.x / Remastered 5.x；不合并脚本、配置或 DLC。",
    ),
    "bethesda_data": (
        "Bethesda 标准 Data 资源",
        "Data",
        "不执行 FOMOD、安装脚本扩展器或自动修改插件载入顺序；ESP/ESM/ESL 与游戏运行时必须匹配。",
    ),
    "bepinex_plugins": (
        "BepInEx 完整 plugins 目录",
        "BepInEx/plugins",
        "必须已有匹配 Mono/IL2CPP、5/6 代及平台架构的 BepInEx；"
        "检测到 core 文件仅代表存在，不代表版本兼容。",
    ),
}


def _text(value: object, maximum: int = 8000) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum or "\0" in value:
        raise ValueError("invalid guide text")
    return value


def _strings(value: object, *, urls: bool = False) -> list[str]:
    if not isinstance(value, list) or len(value) > 500:
        raise ValueError("invalid guide list")
    result = [_text(item) for item in value]
    if urls:
        for item in result:
            parsed = urlsplit(item)
            if (
                parsed.scheme != "https"
                or not parsed.hostname
                or parsed.username
                or parsed.password
                or parsed.port
                or any(c in item for c in "\r\n\\")
            ):
                raise ValueError("invalid source URL")
    return result


class InstallGuides:
    def __init__(self, plugin_dir: Path) -> None:
        self.path = plugin_dir / "data/install_guides.json"
        self._games: list[dict] | None = None
        self._lock = threading.RLock()

    def _load(self) -> list[dict]:
        with self._lock:
            if self._games is not None:
                return self._games
            try:
                if self.path.is_symlink() or self.path.stat().st_size > 8 * 1024 * 1024:
                    raise ValueError("unsafe guide file")
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if (
                    raw.get("schema_version") != 1
                    or not isinstance(raw.get("games"), list)
                    or not 1 <= len(raw["games"]) <= 500
                ):
                    raise ValueError("invalid guide registry")
                ids, apps, games = set(), set(), []
                for item in raw["games"]:
                    game_id = _text(item.get("game_id"), 80)
                    app_ids = _strings(item.get("steam_app_ids"))
                    if (
                        not _IDENT.fullmatch(game_id)
                        or game_id in ids
                        or not app_ids
                        or any(
                            not re.fullmatch(r"[1-9][0-9]{0,9}", a) or a in apps for a in app_ids
                        )
                    ):
                        raise ValueError("ambiguous guide identity")
                    ids.add(game_id)
                    apps.update(app_ids)
                    method_ids, methods = set(), []
                    if not isinstance(item.get("methods"), list) or len(item["methods"]) > 100:
                        raise ValueError("invalid methods")
                    for method in item["methods"]:
                        ident = _text(method.get("id"), 80)
                        if (
                            not _IDENT.fullmatch(ident)
                            or ident in method_ids
                            or ident.startswith("profile-")
                        ):
                            raise ValueError("invalid method identity")
                        method_ids.add(ident)
                        methods.append(
                            {
                                "id": ident,
                                "label": _text(method.get("label")),
                                "versions": _strings(method.get("versions")),
                                "format": _text(method.get("format")),
                                "destination": _text(method.get("destination")),
                                "requirements": _strings(method.get("requirements")),
                                "source_urls": _strings(method.get("source_urls"), urls=True),
                                "can_install": False,
                                "install_mode": None,
                            }
                        )
                    games.append(
                        {
                            "game_id": game_id,
                            "name": _text(item.get("name")),
                            "steam_app_ids": app_ids,
                            "checked_at": _text(item.get("checked_at", raw.get("checked_at"))),
                            "notes": _strings(item.get("notes", [])),
                            "sources": _strings(item.get("sources"), urls=True),
                            "methods": methods,
                        }
                    )
                self._games = games
            except (OSError, ValueError, TypeError, AttributeError, UnicodeError, RecursionError):
                raise ModsError("安装指南数据无法验证，请重新安装完整插件包") from None
            return self._games

    def for_game(self, game: dict) -> dict:
        apps = {str(a) for a in game.get("steam_app_ids", [])}
        if game.get("app_id"):
            apps.add(str(game["app_id"]))
        found = [
            item
            for item in self._load()
            if item["game_id"] == game["id"] or apps.intersection(item["steam_app_ids"])
        ]
        if len(found) > 1:
            raise ModsError("此游戏存在多个版本身份，请重新扫描后选择明确版本")
        if not found:
            return {
                "game_id": game["id"],
                "name": game.get("name", game["id"]),
                "checked_at": "",
                "notes": ["此游戏尚无经过核实的安装指南；仅在作者明确要求时使用手动根目录安装。"],
                "sources": [],
                "methods": [],
            }
        result = copy.deepcopy(found[0])
        result["game_id"] = game["id"]
        # Fixed code defines permissions; research data and client-supplied paths do not.
        for handler, allowed in _PROFILE_APPS.items():
            if handler not in HANDLERS or not apps.intersection(allowed):
                continue
            label, destination, requirement = _PROFILE_INFO[handler]
            ident = "profile-" + handler.replace("_", "-")
            result["methods"].insert(
                0,
                {
                    "id": ident,
                    "label": label,
                    "versions": ["须与下列原始指南及 MOD 作者的版本要求匹配"],
                    "format": handler,
                    "destination": destination,
                    "requirements": [
                        requirement,
                        "只部署经过预览的文件；尚无该游戏的 Steam Deck 实机验证。",
                    ],
                    "source_urls": list(result["sources"][:5]),
                    "can_install": True,
                    "install_mode": "method:" + ident,
                },
            )
        return result

    def resolve_mode(self, game: dict, mode: str) -> str:
        if (
            not isinstance(mode, str)
            or not mode.startswith("method:")
            or not _IDENT.fullmatch(mode[7:])
        ):
            raise ModsError("安装方案无效，请重新选择")
        method = next(
            (
                m
                for m in self.for_game(game)["methods"]
                if m["install_mode"] == mode and m["can_install"]
            ),
            None,
        )
        if method is None or method["format"] not in HANDLERS:
            raise ModsError("此方案不属于所选游戏，或需要使用外部工具")
        return method["format"]
