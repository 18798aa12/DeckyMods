"""Explicit reviewed installation profiles; game-root mode stays separate."""

from pathlib import Path

from .adapters import _blocked, _inventory
from .errors import ModsError
from .paths import relative_path
from .profile_layouts import path_layout
from .profile_smapi import smapi_layout

HANDLERS = frozenset(
    {
        "smapi",
        "cyberpunk_archive",
        "witcher3_mods",
        "bethesda_data",
        "bepinex_plugins",
    }
)


def _target(root: Path, relative: str) -> str:
    parts = relative_path(relative).split("/")
    current, result = root, []
    for index, part in enumerate(parts):
        if current.is_dir():
            matches = [p for p in current.iterdir() if p.name.casefold() == part.casefold()]
            if len(matches) > 1:
                raise ModsError("游戏目录存在大小写冲突，无法安全部署")
            if matches:
                match = matches[0]
                if (
                    match.is_symlink()
                    or (index < len(parts) - 1 and not match.is_dir())
                    or (index == len(parts) - 1 and not match.is_file())
                ):
                    raise ModsError("目标目录包含符号链接或文件类型冲突")
                part = match.name
        result.append(part)
        current = current / part
    return "/".join(result)


def _marker(root: Path, relative: str) -> bool:
    try:
        candidate = root / _target(root, relative)
        return candidate.is_file() and not candidate.is_symlink()
    except ModsError:
        return False


def plan_profile(game: dict, extracted: Path, handler: str) -> dict:
    requirements = list(game.get("requirements", []))
    try:
        if handler not in HANDLERS:
            raise ModsError("此方案需要专用工具，尚未实现文件部署")
        if (
            not game.get("installed")
            or not game.get("path")
            or game.get("running")
            or game.get("updating")
        ):
            raise ModsError("请确认游戏已安装，退出游戏并等待 Steam 更新完成")
        root = Path(game["path"])
        if not root.is_absolute() or not root.is_dir() or root.is_symlink():
            raise ModsError("游戏根目录已变化，请重新扫描")
        paths = _inventory(extracted)
        for path in paths:
            relative_path(str(path))
            if any(p.casefold() == "fomod" for p in path.parts) or path.suffix.casefold() in {
                ".exe",
                ".msi",
                ".bat",
                ".cmd",
                ".ps1",
                ".sh",
                ".com",
            }:
                raise ModsError("该包包含安装器或可选脚本，请使用手动版本/外部工具，不会自动执行")
        if handler == "smapi" and not any(
            _marker(root, p)
            for p in ("StardewModdingAPI", "StardewModdingAPI.exe", "StardewModdingAPI.dll")
        ):
            raise ModsError("请先安装与游戏版本匹配的 SMAPI，再导入其 MOD")
        if handler == "bepinex_plugins" and not any(
            _marker(root, p) for p in ("BepInEx/core/BepInEx.dll", "BepInEx/core/BepInEx.Core.dll")
        ):
            raise ModsError("请先安装匹配 Mono/IL2CPP 及平台架构的 BepInEx，插件不负责安装加载器")
        if handler == "smapi":
            files, declared = smapi_layout(extracted, paths)
            requirements = [*requirements, *declared]
        else:
            files = path_layout(paths, handler, game)
        if handler == "bepinex_plugins":
            requirements = [
                *requirements,
                "仅检测到 BepInEx 核心文件；未验证 Mono/IL2CPP、平台架构或版本是否匹配。",
            ]
        normalized = [{**row, "target": _target(root, row["target"])} for row in files]
        if len({row["target"].casefold() for row in normalized}) != len(normalized):
            raise ModsError("方案产生重复目标，请单独选择所需版本")
        return {
            "files": normalized,
            "warnings": [
                "仅按所选方案部署文件，尚未进行该游戏的 Steam Deck 实机验证。",
                "请确认游戏分支和依赖匹配；不会自动配置载入顺序、执行安装器或合并设置。",
            ],
            "requirements": requirements,
            "blocked_reason": None,
        }
    except (ModsError, OSError, ValueError) as error:
        return _blocked(
            str(error) if isinstance(error, ModsError) else "暂存文件或目标目录已变化，请重新导入",
            requirements,
        )
