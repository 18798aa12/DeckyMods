"""Validated, bundled game mappings; never accept deployment paths from the UI."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath

from .errors import ModsError

_IDENT = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
_ADAPTERS = {"catalog", "ue_pak", "reframework", "re_legacy"}
_CONFIG_KEYS = {
    "pak_dir",
    "native_config",
    "re_pak_prefix",
    "re_base_pak",
    "legacy_root",
    "legacy_mode",
}


def _safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in value.split("/"))


def load_catalog(plugin_dir: Path) -> list[dict]:
    """Load the reviewed registry and fail closed on malformed or unsafe mappings."""
    try:
        path = plugin_dir / "data" / "games.json"
        if path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("oversized catalog")
        items = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(items, list) or not 50 <= len(items) <= 1000:
            raise ValueError("invalid catalog size")
        seen: set[str] = set()
        series: set[str] = set()
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("invalid game")
            for key in ("id", "series"):
                if not isinstance(item.get(key), str) or not _IDENT.fullmatch(item[key]):
                    raise ValueError("invalid identity")
            domain = item.get("nexus_domain")
            if not isinstance(domain, str) or (domain and not _IDENT.fullmatch(domain)):
                raise ValueError("invalid Nexus mapping")
            if item["id"] in seen:
                raise ValueError("duplicate game")
            seen.add(item["id"])
            series.add(item["series"])
            for key in ("name", "series_name", "validation"):
                if not isinstance(item.get(key), str) or not 1 <= len(item[key]) <= 500:
                    raise ValueError("invalid description")
            apps = item.get("steam_app_ids")
            if (
                not isinstance(apps, list)
                or not apps
                or any(
                    not isinstance(app, str) or not re.fullmatch(r"[1-9][0-9]{0,9}", app)
                    for app in apps
                )
            ):
                raise ValueError("invalid Steam identity")
            if item.get("adapter") not in _ADAPTERS:
                raise ValueError("unknown adapter")
            if item.get("support") not in {"automatic", "needs_setup", "catalog"}:
                raise ValueError("invalid capability")
            if (item["adapter"] == "catalog") != (item["support"] == "catalog"):
                raise ValueError("inconsistent capability")
            for key in ("sources", "requirements"):
                values = item.get(key)
                if (
                    not isinstance(values, list)
                    or not values
                    or any(
                        not isinstance(value, str) or not value or len(value) > 2000
                        for value in values
                    )
                ):
                    raise ValueError("missing evidence")
            if any(not source.startswith("https://") for source in item["sources"]):
                raise ValueError("invalid source")
            config = item.get("adapter_config", {})
            if not isinstance(config, dict) or set(config) - _CONFIG_KEYS:
                raise ValueError("invalid adapter config")
            if any(not _safe_relative(value) for value in config.values()):
                raise ValueError("unsafe adapter config")
            if item["adapter"] == "ue_pak" and not config.get("pak_dir"):
                raise ValueError("missing PAK destination")
        if len(series) < 50:
            raise ValueError("fewer than 50 distinct series")
        return items
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        raise ModsError("游戏适配目录损坏，请重新安装插件") from exc
