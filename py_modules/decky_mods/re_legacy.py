"""Conservative existing-resource replacements for pre-RE Engine Steam titles.

These mappings describe authors' public installation facts, not Fluffy's
implementation. They never unpack, repack, patch, rename, or delete game archives.
"""

from __future__ import annotations

import stat
from pathlib import Path, PurePosixPath

from .errors import ModsError

_ROOTS = {
    "residentevil0biohazard0hdremaster": "nativePC",
    "residentevilbiohazardhdremaster": "nativePC",
    "residentevil4": "BIO4",
    "residentevil5": "nativePC_MT",
    "residentevil6": "nativePC",
    "residentevilrevelations": "nativePC",
    "residentevilrevelations2": "nativePC",
}
_RESOURCE_EXTENSIONS = frozenset(
    {
        ".arc",
        ".arc0",
        ".tex",
        ".lmt",
        ".mod",
        ".mrl",
        ".rtex",
        ".gmd",
        ".xwb",
        ".xsb",
        ".ogg",
        ".wav",
        ".sngw",
        ".wmv",
        ".sfd",
        ".usm",
        ".dds",
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tga",
        ".txt",
        ".xml",
        ".dat",
        ".bin",
        ".pack",
        ".lfs",
        ".yz2",
        ".udas",
        ".das",
        ".eff",
        ".tpl",
        ".seq",
        ".mot",
        ".bml",
        ".efl",
        ".rbd",
        ".rvt",
        ".lat",
    }
)
_KNOWN_ANCHORS = frozenset({"nativepc", "nativepc_mt", "bio4", "natives", "reframework"})
_VALIDATION = "仅自动管理已存在的资源文件替换；安装结构已检查，尚未逐款进行 Steam Deck 游戏内验证。"
_DEPENDENCIES = "资源 MOD 仍须满足作者列出的游戏版本、DLC、模型修复补丁和其他前置要求。"


def _blocked(reason: str, requirements: list[str]) -> dict:
    return {"files": [], "warnings": [], "requirements": requirements, "blocked_reason": reason}


def _existing(root: Path, parts: tuple[str, ...], *, directory: bool = False) -> Path:
    """Resolve each case-insensitive segment to an existing unambiguous regular entry."""
    current = root
    for index, part in enumerate(parts):
        matches = [entry for entry in current.iterdir() if entry.name.casefold() == part.casefold()]
        if len(matches) != 1:
            raise ModsError("未找到唯一的原版目标文件或目录；不猜测路径，也不创建新资源文件")
        current = matches[0]
        mode = current.lstat().st_mode
        needs_directory = index < len(parts) - 1 or directory
        if stat.S_ISLNK(mode) or not (
            stat.S_ISDIR(mode) if needs_directory else stat.S_ISREG(mode)
        ):
            raise ModsError("游戏目标包含链接、特殊文件或目录冲突，无法安全替换")
    return current


def _safe_path(path: PurePosixPath) -> bool:
    return (
        bool(path.parts)
        and not path.is_absolute()
        and all(
            not part.startswith(".") and "\\" not in part and "\x00" not in part
            for part in path.parts
        )
    )


def _metadata(path: PurePosixPath, wrapper: str | None) -> bool:
    parent = path.parts[:-1]
    if parent not in ((), (wrapper,) if wrapper is not None else ()):
        return False
    name = path.name.casefold()
    if name in {"modinfo.ini", "desktop.ini"}:
        return True
    if path.suffix.casefold() in {".txt", ".md", ".pdf"}:
        return name.startswith(("readme", "license", "credits"))
    return path.stem.casefold() in {"showcase", "screenshot", "preview"} and (
        path.suffix.casefold() in {".jpg", ".jpeg", ".png", ".webp"}
    )


def _archive_files(
    paths: list[PurePosixPath], anchor: str
) -> list[tuple[PurePosixPath, tuple[str, ...]]]:
    candidates: list[tuple[PurePosixPath, tuple[str, ...]]] = []
    prefixes: set[tuple[str, ...]] = set()
    for path in paths:
        if not isinstance(path, PurePosixPath) or not _safe_path(path):
            raise ModsError("MOD 包包含不安全路径")
        lowered = tuple(part.casefold() for part in path.parts)
        indices = [index for index, part in enumerate(lowered) if part in _KNOWN_ANCHORS]
        if not indices:
            continue
        if len(indices) != 1 or indices[0] > 1 or lowered[indices[0]] != anchor.casefold():
            raise ModsError("MOD 包包含错误游戏目录或多个可选层级，请只导入所选游戏的单一版本")
        index = indices[0]
        if len(path.parts) <= index + 1:
            raise ModsError("MOD 资源路径不完整")
        prefixes.add(path.parts[: index + 1])
        candidates.append((path, (anchor, *path.parts[index + 1 :])))
    if len(prefixes) != 1 or not candidates:
        raise ModsError("需要明确的游戏资源目录和单一可选版本，不能从裸文件猜测安装位置")
    prefix = next(iter(prefixes))
    wrapper = prefix[0] if len(prefix) == 2 else None
    selected = {path for path, _ in candidates}
    if any(path not in selected and not _metadata(path, wrapper) for path in paths):
        raise ModsError("MOD 混有未适配文件、加载器或安装器；请按作者说明分开安装")
    return candidates


def _packed_override(root: Path, target: Path) -> bool:
    if target.suffix.casefold() == ".lfs":
        return False
    names = {target.name.casefold() + suffix for suffix in (".lfs", ".yz2.lfs")}
    return any(entry.name.casefold() in names for entry in target.parent.iterdir())


def plan_legacy(game: dict, paths: list[PurePosixPath], root: Path) -> dict:
    """Return existing game resource mappings without changing any game file."""
    requirements = [*game.get("requirements", []), _DEPENDENCIES]
    game_id = game.get("id")
    anchor = _ROOTS.get(game_id)
    config = game.get("adapter_config", {})
    if (
        anchor is None
        or config.get("legacy_root") != anchor
        or config.get("legacy_mode") != "replacement"
    ):
        return _blocked("此游戏或资源目录尚无可信的旧引擎替换适配", requirements)
    if game_id == "residentevil4":
        requirements.append(
            "RE4 原版 UHD 的 re4_tweaks 位于 Bin32；"
            "如使用它，需要独立安装对应加载器及 dinput8 启动项。"
        )
    try:
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise ModsError("游戏安装目录无效，请刷新游戏列表")
        _existing(root, (anchor,), directory=True)
        candidates = _archive_files(paths, anchor)
        files: list[dict[str, str]] = []
        targets: set[str] = set()
        for source, relative in candidates:
            if source.suffix.casefold() not in _RESOURCE_EXTENSIONS:
                raise ModsError("仅支持已适配资源文件；DLL、脚本、安装器和补丁程序需要专用安装")
            target = _existing(root, relative)
            if game_id == "residentevil4" and _packed_override(root, target):
                raise ModsError(
                    "此 RE4 松散资源仍被 LFS 归档覆盖，需要作者指定的归档处理；未修改文件"
                )
            target_name = target.relative_to(root).as_posix()
            if target_name.casefold() in targets:
                raise ModsError("MOD 包包含重复或大小写冲突的目标文件")
            targets.add(target_name.casefold())
            files.append({"source": str(source), "target": target_name})
    except ModsError as error:
        return _blocked(str(error), requirements)
    except OSError:
        return _blocked("读取游戏资源目录失败，请检查文件权限并重新刷新", requirements)
    warnings = [
        _VALIDATION,
        "将备份并覆盖预览中的原版资源；禁用或卸载时恢复，不能合并同一 ARC 内部的改动。",
    ]
    if game_id == "residentevil4":
        warnings.append(
            "不会删除或重命名 LFS、解包归档、修改 EXE；需要这些操作的 MOD 不在自动安装范围内。"
        )
    return {
        "files": files,
        "warnings": warnings,
        "requirements": list(dict.fromkeys(requirements)),
        "blocked_reason": None,
    }
