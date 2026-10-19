"""Conservative archive layout adapters with registry-owned destinations."""

from __future__ import annotations

import os
import stat
from pathlib import Path, PurePosixPath

from .errors import ModsError
from .re_engine import plan_re_engine
from .re_legacy import plan_legacy

_METADATA = {".txt", ".md", ".jpg", ".jpeg", ".png", ".webp", ".gif"}
_PAK_EXTENSIONS = {".pak", ".ucas", ".utoc", ".sig"}
_SETUP = "插件会检查并合并 WINEDLLOVERRIDES 的 dinput8 参数；请查看游戏的“启动项”状态"
_VALIDATION = "已验证安装结构；尚未在 Steam Deck 游戏内验证，游戏更新后可能需要匹配新版 MOD。"


def _blocked(reason: str, requirements: list[str]) -> dict:
    return {"files": [], "warnings": [], "requirements": requirements, "blocked_reason": reason}


def _inventory(extracted: Path) -> list[PurePosixPath]:
    if extracted.is_symlink() or not extracted.is_dir():
        raise ModsError("MOD 暂存目录无效，请重新导入")
    result: list[PurePosixPath] = []
    for folder, directories, files in os.walk(extracted, followlinks=False):
        for name in [*directories, *files]:
            path = Path(folder) / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ModsError("MOD 包包含链接或特殊文件，无法安全安装")
            if any(char in name for char in "\\\x00") or name in {".", ".."}:
                raise ModsError("MOD 包包含不安全文件名")
        for name in files:
            rel = PurePosixPath((Path(folder) / name).relative_to(extracted).as_posix())
            if any(part.startswith(".") for part in rel.parts):
                raise ModsError("MOD 包包含隐藏路径，请移除后重新导入")
            result.append(rel)
            if len(result) > 20000:
                raise ModsError("MOD 包文件过多，请拆分后导入")
    return sorted(result, key=str)


def _is_metadata(path: PurePosixPath) -> bool:
    return path.suffix.lower() in _METADATA or path.name.lower() in {"modinfo.ini", "desktop.ini"}


def _target_case(root: Path, relative: str) -> str:
    """Match installed Linux directory casing, rejecting ambiguous/symlinked paths."""
    parts = PurePosixPath(relative).parts
    current = root
    selected: list[str] = []
    for part in parts:
        actual = part
        if current.is_dir():
            matches = [
                entry for entry in current.iterdir() if entry.name.casefold() == part.casefold()
            ]
            if len(matches) > 1:
                raise ModsError("游戏目录包含大小写冲突，无法安全部署")
            if matches:
                match = matches[0]
                if match.is_symlink() or not match.is_dir():
                    raise ModsError("MOD 目标目录包含链接或文件冲突")
                actual = match.name
        selected.append(actual)
        current = current / actual
    return "/".join(selected)


def _ue_pak(game: dict, paths: list[PurePosixPath], root: Path) -> dict:
    requirements = list(game["requirements"])
    payload = [path for path in paths if path.suffix.lower() in _PAK_EXTENSIONS]
    if not payload or any(not _is_metadata(path) and path not in payload for path in paths):
        return _blocked(
            "仅支持普通 PAK 资源包；脚本、安装器、存档和配置包需要专用适配", requirements
        )
    if any("logicmods" in (part.lower() for part in path.parts) for path in payload):
        return _blocked("检测到 LogicMods 蓝图 MOD，需要对应加载器和专用安装方式", requirements)
    config = game["adapter_config"]
    destination = config["pak_dir"]
    expected_game = PurePosixPath(destination).parts[0].casefold()
    for path in payload:
        lowered = [part.casefold() for part in path.parts]
        if "content" in lowered and "paks" in lowered:
            index = lowered.index("content")
            if index == 0 or lowered[index - 1] != expected_game:
                return _blocked("MOD 包目录与所选游戏不匹配，请选择正确游戏", requirements)
    # Plain files or one wrapper are safe. Distinct option directories need a user choice first.
    anchors = [
        next((i for i, part in enumerate(path.parts) if part.casefold() == "~mods"), None)
        for path in payload
    ]
    if any(anchor is not None for anchor in anchors) and not all(
        anchor is not None for anchor in anchors
    ):
        return _blocked("MOD 包混合多种目录结构，请导入单一资源包", requirements)
    anchor_roots = {
        str(PurePosixPath(*path.parts[: anchor + 1])).casefold()
        for path, anchor in zip(payload, anchors, strict=True)
        if anchor is not None
    }
    if len(anchor_roots) > 1:
        return _blocked("MOD 包包含多个可选目录，请先选择并单独导入所需版本", requirements)
    if (
        all(anchor is None for anchor in anchors)
        and len({str(path.parent) for path in payload}) != 1
    ):
        return _blocked("MOD 包包含多个可选目录，请先选择并单独导入所需版本", requirements)
    relative = [
        (
            path,
            PurePosixPath(*path.parts[anchor + 1 :])
            if anchor is not None
            else PurePosixPath(path.name),
        )
        for path, anchor in zip(payload, anchors, strict=True)
    ]
    groups: dict[str, set[str]] = {}
    targets: set[str] = set()
    for _, target in relative:
        lowered = str(target).casefold()
        if lowered in targets:
            return _blocked("MOD 包包含重复或大小写冲突的文件", requirements)
        targets.add(lowered)
        groups.setdefault(str(target.with_suffix("")).casefold(), set()).add(target.suffix.lower())
    for extensions in groups.values():
        if ".pak" not in extensions or (
            extensions & {".utoc", ".ucas"} and not {".pak", ".utoc", ".ucas"} <= extensions
        ):
            return _blocked("PAK 包不完整，.pak/.ucas/.utoc 必须保留对应文件", requirements)
    destination = _target_case(root, destination)
    files = [
        {"source": str(source), "target": f"{destination}/{target}"} for source, target in relative
    ]
    warnings = [_VALIDATION]
    if len(groups) > 1:
        warnings.append("压缩包包含多个资源包，预览中的所有资源包都会启用；请确认不是互斥版本。")
    return {
        "files": files,
        "warnings": warnings,
        "requirements": requirements,
        "blocked_reason": None,
    }


def plan_files(game: dict, extracted: Path) -> dict:
    """Inspect supported layouts; return only relative paths, never write into the game."""
    if not game.get("installed") or not isinstance(game.get("path"), str):
        raise ModsError("未找到可验证的游戏安装目录")
    if game.get("running"):
        raise ModsError("请先完全退出游戏，再安装、启用或停用 MOD")
    root = Path(game["path"])
    if not root.is_absolute() or not root.is_dir() or root.is_symlink():
        raise ModsError("游戏安装目录已变更，请刷新游戏列表")
    paths = _inventory(extracted)
    adapter = game.get("adapter")
    if adapter == "ue_pak":
        return _ue_pak(game, paths, root)
    if adapter == "reframework":
        return plan_re_engine(game, paths, root)
    if adapter == "re_legacy":
        return plan_legacy(game, paths, root)
    return _blocked(
        "此游戏尚无自动安装适配；请按作者说明准备本地压缩包，并明确选择根目录安装",
        list(game["requirements"]),
    )
