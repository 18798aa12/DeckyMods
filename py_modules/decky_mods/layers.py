"""Compute the effective file stack without mutating previous MOD records."""

import re
from pathlib import Path

from .errors import ModsError
from .paths import relative_path


def effective_files(game: dict, state: dict, mods: list[dict]) -> dict[str, str]:
    result: dict[str, str] = {}
    paks: list[dict] = []
    for mod in mods:
        if not mod["enabled"]:
            continue
        for file in mod["files"]:
            if file.get("kind") == "re_pak":
                paks.append(file)
            else:
                result[relative_path(file["target"])] = file["hash"]
    if paks:
        prefix = game.get("adapter_config", {}).get("re_pak_prefix") or game.get("pak_prefix")
        padding = game.get("pak_padding", 3)
        if (
            not isinstance(prefix, str)
            or not re.fullmatch(r"[a-zA-Z0-9_]+\.pak\.patch_", prefix)
            or padding not in (3,)
        ):
            raise ModsError("此游戏的 PAK 版本或命名尚未适配")
        pattern = re.compile(re.escape(prefix) + r"(\d{3})\.pak$", re.IGNORECASE)
        official = []
        for path in Path(game["path"]).iterdir():
            match = pattern.fullmatch(path.name)
            if match and path.name not in state["managed"]:
                official.append(int(match[1]))
        start = max(official, default=0) + 1
        if start + len(paks) > 1000:
            raise ModsError("RE PAK 补丁数量超过已适配范围")
        for offset, file in enumerate(paks):
            name = f"{prefix}{start + offset:03}.pak"
            if name in result:
                raise ModsError("PAK 与普通文件的目标冲突，请分别安装")
            result[name] = file["hash"]
    return result
