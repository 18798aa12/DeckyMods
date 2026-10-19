"""Explicit, reversible root-relative layouts for games without an adapter."""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

from .adapters import _inventory
from .errors import ModsError
from .paths import relative_path

_ROOT_WARNING = (
    "此游戏尚无专用适配：只有作者明确要求解压到游戏根目录时才使用此选项。"
    "所有相对路径原样保留，不剥除外层目录；请核对文件预览。"
)
_MANUAL_WARNING = (
    "此模式不会安装前置、合并配置或自动添加启动项；"
    "安装结构不代表兼容性，游戏版本和依赖仍须符合作者说明。"
)
_LOADER_WARNING = (
    "包内包含 DLL/ASI/SO 加载器：游戏可能执行这些文件；"
    "请确认来源、版本和作者要求的启动项，插件不会执行安装器。"
)
_EXECUTABLE_SUFFIXES = frozenset(
    {
        ".exe",
        ".com",
        ".msi",
        ".msp",
        ".msix",
        ".msixbundle",
        ".bat",
        ".cmd",
        ".ps1",
        ".psm1",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".command",
        ".vbs",
        ".vbe",
        ".wsf",
        ".wsh",
        ".hta",
        ".desktop",
        ".lnk",
        ".url",
        ".scr",
        ".app",
        ".pkg",
        ".deb",
        ".rpm",
        ".run",
    }
)
_LIBRARY_ROOTS = frozenset({"steamapps", "compatdata", "userdata", "shadercache", "pfx"})
_SYSTEM_DIRECTORIES = frozenset({"__macosx", "$recycle.bin", "system volume information"})
_OPTION_WORDS = frozenset(
    {
        "fomod",
        "option",
        "options",
        "optional",
        "variant",
        "variants",
        "alternative",
        "alternatives",
        "installer",
        "installers",
    }
)
_VERSION_FAMILIES = (
    frozenset({"dx11", "dx12", "directx11", "directx12"}),
    frozenset({"x86", "x64", "32bit", "64bit", "32 bit", "64 bit"}),
    frozenset({"rt", "non rt", "nort"}),
)


def _blocked(reason: str, requirements: list[str]) -> dict:
    return {
        "files": [],
        "warnings": [_ROOT_WARNING, _MANUAL_WARNING],
        "requirements": requirements,
        "blocked_reason": reason,
    }


def _normalized_name(name: str) -> str:
    normalized = re.sub(r"[_-]+", " ", name.casefold()).strip()
    return re.sub(r"^\d+[.\s]+", "", normalized)


def _directory_reason(parts: tuple[str, ...]) -> str | None:
    for part in parts:
        name = _normalized_name(part)
        if name.split(" ", 1)[0] in _OPTION_WORDS:
            return "检测到 FOMOD、安装器或可选版本目录；请先按作者说明选择单一根目录版本"
        if part.casefold() in _SYSTEM_DIRECTORIES or Path(part).suffix.casefold() == ".app":
            return "MOD 包包含系统目录或应用安装包，请仅导入作者要求放入游戏根目录的文件"
    if parts and parts[0].casefold() in _LIBRARY_ROOTS:
        return "压缩包指向 Steam 库或 Proton 前缀；根目录模式仅管理所选游戏内部的文件"
    return None


def _walk_error(error: OSError) -> None:
    raise ModsError("MOD 暂存目录无法完整读取，请重新导入") from error


def _inspect_layout(extracted: Path, paths: list[PurePosixPath]) -> str | None:
    """Validate directories too, including empty hidden or option directories."""
    siblings: dict[str, set[str]] = {}
    for folder, directories, _ in os.walk(extracted, followlinks=False, onerror=_walk_error):
        parent = Path(folder).relative_to(extracted)
        siblings[parent.as_posix()] = {_normalized_name(name) for name in directories}
        for name in directories:
            relative = (parent / name).as_posix()
            safe = relative_path(relative)
            reason = _directory_reason(PurePosixPath(safe).parts)
            if reason:
                return reason
    if any(len(names & family) > 1 for names in siblings.values() for family in _VERSION_FAMILIES):
        return "压缩包包含多个运行时或游戏版本目录；请单独导入作者指定的版本"
    casing: dict[str, str] = {}
    for path in paths:
        safe = relative_path(str(path))
        if safe != str(path):
            raise ModsError("MOD 路径需要规范化，请整理压缩包后重新导入")
        for index in range(1, len(path.parts) + 1):
            prefix = str(PurePosixPath(*path.parts[:index]))
            previous = casing.get(prefix.casefold())
            if previous is not None and previous != prefix:
                return "MOD 包包含大小写冲突的文件或目录，请统一后重新导入"
            casing[prefix.casefold()] = prefix
        reason = _directory_reason(path.parts[:-1])
        if reason:
            return reason
        if path.suffix.casefold() in _EXECUTABLE_SUFFIXES:
            return "根目录模式不支持安装器或可执行安装脚本；请导入安装后应放入游戏目录的文件"
        descriptor = os.open(extracted / str(path), os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as stream:
            if stream.read(2) == b"#!":
                return "检测到可执行安装脚本，请按作者说明手动处理后导入游戏文件"
    return None


def _check_existing_case(root: Path, paths: list[PurePosixPath]) -> None:
    inspected: dict[str, dict[str, list[str]]] = {}
    for path in paths:
        current = root
        for part in path.parts:
            if not current.exists():
                break
            if current.is_symlink() or not current.is_dir():
                raise ModsError("MOD 目标目录存在链接或文件冲突")
            key = str(current)
            if key not in inspected:
                entries: dict[str, list[str]] = {}
                for entry in current.iterdir():
                    entries.setdefault(entry.name.casefold(), []).append(entry.name)
                inspected[key] = entries
            matches = inspected[key].get(part.casefold(), [])
            if len(matches) > 1 or matches and matches[0] != part:
                raise ModsError("MOD 路径与游戏现有文件大小写不同，请统一后重新导入")
            current = current / part
            if current.is_symlink():
                raise ModsError("MOD 目标包含符号链接，请先检查游戏目录")


def plan_root_files(game: dict, extracted: Path) -> dict:
    """Plan an explicitly selected catalog-game root layout; never deploy files here."""
    if not game.get("installed") or not isinstance(game.get("path"), str):
        raise ModsError("未找到可验证的游戏安装目录")
    if game.get("running") or game.get("updating"):
        raise ModsError("请先退出游戏并等待 Steam 更新结束，再修改 MOD")
    root = Path(game["path"])
    if not root.is_absolute() or not root.is_dir() or root.is_symlink():
        raise ModsError("游戏安装目录已变更，请刷新游戏列表")
    requirements = list(game.get("requirements", []))
    if game.get("adapter") != "catalog":
        return _blocked("此游戏已有专用适配或身份无效，请使用对应的自动安装模式", requirements)
    try:
        paths = _inventory(extracted)
        if not paths:
            return _blocked("压缩包没有可安装文件", requirements)
        reason = _inspect_layout(extracted, paths)
        if not reason:
            try:
                _check_existing_case(root, paths)
            except ModsError as error:
                reason = str(error)
    except OSError as error:
        raise ModsError("MOD 暂存文件已变更或无法读取，请重新导入") from error
    if reason:
        return _blocked(reason, requirements)
    warnings = [_ROOT_WARNING, _MANUAL_WARNING]
    if any(
        path.suffix.casefold() in {".dll", ".asi", ".so"} or ".so." in path.name.casefold()
        for path in paths
    ):
        warnings = [*warnings, _LOADER_WARNING]
    return {
        "files": [{"source": str(path), "target": str(path)} for path in paths],
        "warnings": warnings,
        "requirements": requirements,
        "blocked_reason": None,
    }
