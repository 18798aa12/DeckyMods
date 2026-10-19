"""SMAPI package identity and declared prerequisites, without executing mods."""

import re
from pathlib import Path, PurePosixPath

from .adapters import _is_metadata
from .errors import ModsError
from .paths import relative_path
from .profile_json import manifest_object


def _text(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 256
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ModsError("SMAPI 清单的身份、版本或依赖字段无效")
    return value.strip()


def _identity(value: object) -> str:
    text = _text(value)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", text):
        raise ModsError("SMAPI 清单含不兼容的 UniqueID")
    return text


def _dependency(value: object, label: str) -> str:
    if not isinstance(value, dict):
        raise ModsError("SMAPI 清单依赖必须包含明确的 UniqueID")
    identity = _identity(value.get("UniqueID"))
    minimum = value.get("MinimumVersion")
    version = f"，至少 {_text(minimum)}" if minimum is not None else ""
    return f"{label} {identity}{version}（来自清单，未验证是否已安装及版本）"


def _prerequisites(info: dict) -> list[str]:
    result = ["仅检测到 SMAPI 入口文件；未验证已安装的 SMAPI、游戏版本或依赖。"]
    for field, label in (
        ("MinimumApiVersion", "SMAPI"),
        ("MinimumGameVersion", "游戏"),
    ):
        if info.get(field) is not None:
            result.append(f"{label} 至少 {_text(info[field])}（来自清单，未验证当前版本）")
    if info.get("ContentPackFor"):
        result.append(_dependency(info["ContentPackFor"], "内容框架"))
    dependencies = info.get("Dependencies", [])
    if not isinstance(dependencies, list) or len(dependencies) > 128:
        raise ModsError("SMAPI 清单依赖列表无效或过多")
    for dependency in dependencies:
        if not isinstance(dependency, dict) or not isinstance(
            dependency.get("IsRequired", True), bool
        ):
            raise ModsError("SMAPI 清单依赖的 IsRequired 字段无效")
        description = _dependency(dependency, "必需依赖")
        if dependency.get("IsRequired", True):
            result.append(description)
    return result


def smapi_layout(extracted: Path, paths: list[PurePosixPath]) -> tuple[list[dict], list[str]]:
    manifests = [p for p in paths if p.name.casefold() == "manifest.json"]
    if len(manifests) != 1:
        raise ModsError("SMAPI 包必须包含一个明确的 manifest.json；可选版本和整合包请先拆分")
    manifest = manifests[0]
    with (extracted / str(manifest)).open("rb") as source:
        raw = source.read(256 * 1024 + 1)
    if len(raw) > 256 * 1024:
        raise ModsError("SMAPI 清单过大")
    info = manifest_object(raw)
    _text(info.get("Name"))
    _text(info.get("Version"))
    identity = _identity(info.get("UniqueID"))
    entry, content = info.get("EntryDll"), info.get("ContentPackFor")
    if entry is not None:
        entry = _text(entry)
    if content is not None:
        _dependency(content, "内容框架")
    if (entry is None) == (content is None):
        raise ModsError("SMAPI 清单必须明确指定 EntryDll 或 ContentPackFor 其中一个")
    if entry:
        if "/" in entry or "\\" in entry or not entry.casefold().endswith(".dll"):
            raise ModsError("SMAPI 清单指定的插件 DLL 路径无效")
    requirements = _prerequisites(info)
    parent = manifest.parent
    name = identity if parent == PurePosixPath(".") else parent.name
    relative_path(name)
    payload = [p for p in paths if p.is_relative_to(parent)]
    if any(p not in payload and not _is_metadata(p) for p in paths):
        raise ModsError("SMAPI 包包含多个目录或未识别文件，请单独导入所需版本")
    if entry and not any(p.relative_to(parent).as_posix() == entry for p in payload):
        raise ModsError("SMAPI 包缺少清单指定的插件 DLL")
    files = [{"source": str(p), "target": f"Mods/{name}/{p.relative_to(parent)}"} for p in payload]
    return files, requirements
