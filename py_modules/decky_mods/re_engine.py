"""Reviewed RE Engine resource layouts, without modifying original game PAKs."""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path, PurePosixPath

CONFIG_NAME = "re2_fw_config.txt"
LOOSE_KEY = "LooseFileLoader_Enabled"
PAK_DIRECTORY_KEY = "IntegrityCheckBypass_LoadPakDirectory"
_CONFIG_LIMIT = 512 * 1024
_MODERN_RE = {
    "residentevil22019",
    "residentevil32020",
    "residentevil42023",
    "residentevil7",
    "residentevilvillage",
    "residentevilrequiem",
}
_BRANCH_GAMES = {"residentevil22019", "residentevil32020", "residentevil7"}
_ANCHORS = {"reframework", "natives", "pak_mods"}
_INSTALLERS = {"fomod", "tslpatchdata"}
_EXECUTABLES = {".exe", ".bat", ".cmd", ".ps1", ".sh", ".msi", ".com", ".scr", ".lnk"}
_SETUP = "插件会检查并合并 WINEDLLOVERRIDES 的 dinput8 参数；请查看游戏的“启动项”状态"
_VALIDATION = "已验证安装结构；尚未在 Steam Deck 游戏内验证，游戏更新后需要匹配新版 MOD。"


def _blocked(reason: str, requirements: list[str]) -> dict:
    return {"files": [], "warnings": [], "requirements": requirements, "blocked_reason": reason}


def _regular(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.lstat().st_mode)
    except OSError:
        return False


def config_status(root: Path) -> dict:
    """Read the shared, flat REFramework config; never follow a link or edit it."""
    path = root / CONFIG_NAME
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return {"exists": False, "valid": False, "flags": {}}
    except OSError:
        return {"exists": True, "valid": False, "flags": {}}
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size > _CONFIG_LIMIT:
            return {"exists": True, "valid": False, "flags": {}}
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            content = handle.read(_CONFIG_LIMIT + 1)
        if len(content) > _CONFIG_LIMIT or b"\x00" in content:
            return {"exists": True, "valid": False, "flags": {}}
        text = content.decode("utf-8-sig")
    except (OSError, UnicodeError):
        return {"exists": True, "valid": False, "flags": {}}
    finally:
        os.close(descriptor)
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";")):
            continue
        key, separator, value = line.partition("=")
        if not separator:
            return {"exists": True, "valid": False, "flags": {}}
        key, value = key.strip(), value.strip().lower()
        if key in {LOOSE_KEY, PAK_DIRECTORY_KEY}:
            if key in values or value not in {"true", "false"}:
                return {"exists": True, "valid": False, "flags": {}}
            values = {**values, key: value}
    return {
        "exists": True,
        "valid": True,
        "flags": {key: values.get(key) == "true" for key in (LOOSE_KEY, PAK_DIRECTORY_KEY)},
    }


def read_reframework_flags(root: Path) -> dict[str, bool]:
    """Return verified flag values, or an empty mapping for an unsafe config."""
    return config_status(root)["flags"]


def _outer_metadata(path: PurePosixPath, wrapper: tuple[str, ...]) -> bool:
    parent = tuple(part.casefold() for part in path.parts[:-1])
    if parent != wrapper[: len(parent)]:
        return False
    name = path.name.casefold()
    if name in {"modinfo.ini", "desktop.ini", "license", "licence"}:
        return True
    if re.fullmatch(r"(?:readme|license|licence)(?:[ _.-][^/]*)?\.(?:txt|md)", name):
        return True
    return bool(
        re.fullmatch(
            r"(?:screenshot|showcase|preview)(?:[ _.-][^/]*)?\.(?:png|jpe?g|webp|gif)", name
        )
    )


def _native_path(path: PurePosixPath, anchor: int) -> PurePosixPath | None:
    tail = path.parts[anchor + 1 :]
    if len(tail) < 2 or tail[0].casefold() not in {"stm", "x64"}:
        return None
    if path.suffix.casefold() in _EXECUTABLES | {".dll", ".lua"}:
        return None
    return PurePosixPath("natives", *tail)


def plan_re_engine(game: dict, paths: list[PurePosixPath], root: Path) -> dict:
    """Plan known scripts, loose resources and supported PAKs; never write to the game."""
    requirements = list(dict.fromkeys([*game["requirements"], _SETUP]))
    if not _regular(root / "dinput8.dll"):
        return _blocked(
            "请先安装匹配游戏版本的官方 REFramework，再检查启动项并运行一次游戏", requirements
        )
    config = game.get("adapter_config", {})
    result: list[dict] = []
    wrappers: set[tuple[str, ...]] = set()
    metadata: list[PurePosixPath] = []
    native_variants: set[str] = set()
    patch_packs = 0
    directory_packs = 0
    for path in paths:
        lowered = tuple(part.casefold() for part in path.parts)
        if (
            path.is_absolute()
            or not lowered
            or any(part in {".", ".."} or "\\" in part or "\x00" in part for part in path.parts)
        ):
            return _blocked("MOD 包包含不安全路径", requirements)
        if any(part in _INSTALLERS for part in lowered):
            return _blocked(
                "此包包含安装器或可选安装脚本，请先选择作者提供的单一手动安装版本", requirements
            )
        anchor = next((index for index, part in enumerate(lowered) if part in _ANCHORS), None)
        if anchor is not None:
            wrappers.add(lowered[:anchor])
            kind = lowered[anchor]
            if kind == "reframework":
                if len(lowered) <= anchor + 2 or lowered[anchor + 1] not in {"autorun", "plugins"}:
                    return _blocked(
                        "REFramework 包仅支持 autorun 脚本和 plugins DLL 目录", requirements
                    )
                if lowered[anchor + 1] == "plugins" and path.suffix.casefold() != ".dll":
                    return _blocked("REFramework plugins 目录仅支持 DLL 插件", requirements)
                if path.suffix.casefold() in _EXECUTABLES:
                    return _blocked("脚本包包含外部安装程序，请按作者说明安装", requirements)
                target = PurePosixPath(
                    "reframework", lowered[anchor + 1], *path.parts[anchor + 2 :]
                )
            elif kind == "natives":
                if game["id"] not in _MODERN_RE:
                    return _blocked("此游戏的 natives 资源格式尚未完成专用适配", requirements)
                target = _native_path(path, anchor)
                if target is None:
                    return _blocked("natives 资源包目录不完整或包含不支持的安装文件", requirements)
                native_variants.add(lowered[anchor + 1])
            else:
                if game["id"] != "residentevilrequiem":
                    return _blocked(
                        "此游戏未确认支持 pak_mods 目录，不能套用 RE9 加载方式", requirements
                    )
                if len(lowered) <= anchor + 1 or path.suffix != ".pak":
                    return _blocked("pak_mods 目录仅支持以小写 .pak 结尾的资源包", requirements)
                target = PurePosixPath("pak_mods", *path.parts[anchor + 1 :])
                directory_packs += 1
            result.append({"source": str(path), "target": str(target)})
        elif path.suffix.casefold() == ".pak":
            wrappers.add(lowered[:-1])
            if game["id"] == "residentevilrequiem" and path.suffix == ".pak":
                directory_packs += 1
                result.append({"source": str(path), "target": f"pak_mods/{path.name}"})
            else:
                prefix = config.get("re_pak_prefix")
                if not prefix or not re.fullmatch(re.escape(prefix) + r"[0-9]{3}\.pak", path.name):
                    return _blocked("此 PAK 名称与已适配的游戏补丁格式不匹配", requirements)
                if not _regular(root / config["re_base_pak"]):
                    return _blocked("未找到匹配的原版 PAK，不能确认游戏归档兼容性", requirements)
                patch_packs += 1
                result.append({"source": str(path), "target": path.name, "kind": "re_pak"})
        else:
            metadata.append(path)
    if not result:
        return _blocked("未找到支持的 REFramework MOD 文件", requirements)
    if len(wrappers) != 1 or len(native_variants) > 1 or patch_packs > 1:
        return _blocked("MOD 包包含多个可选目录或互斥版本，请单独导入所需版本", requirements)
    wrapper = next(iter(wrappers))
    if any(not _outer_metadata(path, wrapper) for path in metadata):
        return _blocked("此包包含未适配的根目录文件或安装器，不能自动覆盖游戏根目录", requirements)
    targets = [item["target"].casefold() for item in result]
    if len(targets) != len(set(targets)):
        return _blocked("MOD 包包含重复部署文件", requirements)
    needed = ([LOOSE_KEY] if native_variants or directory_packs else []) + (
        [PAK_DIRECTORY_KEY] if directory_packs else []
    )
    status = config_status(root) if needed else None
    if status is not None and not status["valid"]:
        return _blocked(
            f"资源 MOD 需要有效的 {CONFIG_NAME}；请先运行一次匹配的 REFramework，"
            "配置重复、损坏或链接文件需先修复",
            requirements,
        )
    missing = [key for key in needed if not status["flags"].get(key)] if status else []
    warnings = [
        _VALIDATION,
        "检测到加载器文件不代表运行成功；请确认其来自官方 REFramework 且匹配当前游戏版本。",
    ]
    if missing:
        warnings.append("确认安装时将自动准备资源加载设置，并备份原配置。")
    if game["id"] in _BRANCH_GAMES:
        warnings.append(
            "此 MOD 必须匹配 RT / 非 RT 游戏分支；目录名称不能证明版本兼容，请核对作者说明。"
        )
    if directory_packs:
        warnings.append(
            "RE9 PAK 需要支持 PAK Directory Loading 的新版 REFramework；完全重启游戏后生效。"
        )
    if directory_packs and native_variants:
        warnings.append("此包同时包含 PAK 和 natives 资源，二者覆盖优先级需以作者说明为准。")
    return {
        "files": result,
        "warnings": warnings,
        "requirements": requirements,
        "blocked_reason": None,
        "config_requirements": missing,
    }
