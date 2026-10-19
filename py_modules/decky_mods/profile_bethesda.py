"""Reviewed Bethesda data identities; unrelated runtimes fail closed."""

from pathlib import PurePosixPath
from typing import NamedTuple

from .errors import ModsError

DATA_ROOTS = frozenset(
    {
        "textures",
        "meshes",
        "scripts",
        "interface",
        "sound",
        "music",
        "seq",
        "skse",
        "f4se",
        "fose",
        "nvse",
        "obse",
        "menus",
        "strings",
        "materials",
        "geometries",
        "video",
    }
)
_EXTENDERS = frozenset({"skse", "f4se", "fose", "nvse", "obse", "sfse", "mwse"})
_UNREVIEWED = frozenset(
    {
        "morrowind",
        "starfield",
        "oblivionremastered",
        "fallout4vr",
        "enderal",
        "enderalspecialedition",
    }
)


class DataIdentity(NamedTuple):
    names: frozenset[str]
    steam_ids: frozenset[str]
    extender: str
    archive: str
    esl: bool = False


_IDENTITIES = (
    DataIdentity(frozenset({"skyrim"}), frozenset({"72850"}), "skse", ".bsa"),
    DataIdentity(
        frozenset({"skyrimspecialedition", "skyrimse"}),
        frozenset({"489830"}),
        "skse",
        ".bsa",
        True,
    ),
    DataIdentity(frozenset({"skyrimvr"}), frozenset({"611670"}), "skse", ".bsa"),
    DataIdentity(frozenset({"fallout3"}), frozenset({"22300", "22370"}), "fose", ".bsa"),
    DataIdentity(
        frozenset({"falloutnv", "newvegas"}), frozenset({"22380", "22490"}), "nvse", ".bsa"
    ),
    DataIdentity(frozenset({"fallout4"}), frozenset({"377160"}), "f4se", ".ba2", True),
    DataIdentity(frozenset({"oblivion"}), frozenset({"22330"}), "obse", ".bsa"),
)


def _identity(game: dict) -> DataIdentity:
    name = str(game.get("id", "")).casefold()
    app_ids = game.get("steam_app_ids", [])
    if not isinstance(app_ids, list) or any(not isinstance(value, str) for value in app_ids):
        raise ModsError("游戏身份无效，请重新扫描")
    named = [identity for identity in _IDENTITIES if name in identity.names]
    matched = [identity for identity in _IDENTITIES if identity.steam_ids.intersection(app_ids)]
    if (
        name in _UNREVIEWED
        or len(matched) > 1
        or app_ids
        and not matched
        or named
        and matched
        and named[0] != matched[0]
    ):
        raise ModsError("此游戏或分支尚未审核 Data 部署，或游戏身份不一致")
    selected = named or matched
    if not selected:
        raise ModsError("此游戏尚未审核 Data 部署，请使用专用说明或手动根目录预览")
    return selected[0]


def data_layout(items: list[tuple[PurePosixPath, PurePosixPath]], game: dict) -> list[dict]:
    identity = _identity(game)
    for source, tail in items:
        lower = tuple(part.casefold() for part in tail.parts)
        prefix = source.parts[: len(source.parts) - len(tail.parts) - 1] if source != tail else ()
        for wrapper in prefix:
            wrapper_name = wrapper.casefold().replace(" ", "").replace("-", "").replace("_", "")
            named = [entry for entry in _IDENTITIES if wrapper_name in entry.names]
            if wrapper_name in _UNREVIEWED or named and named[0] != identity:
                raise ModsError("压缩包明确属于另一个游戏，不能应用当前 Data 方案")
        if lower[0] in _EXTENDERS and lower[0] != identity.extender:
            raise ModsError("检测到其它游戏的脚本扩展目录，请选择正确游戏与版本")
        extension = tail.suffix.casefold()
        if extension in {".ba2", ".bsa"} and extension != identity.archive:
            raise ModsError("资源归档格式与所选游戏不匹配")
        if extension == ".esl" and not identity.esl:
            raise ModsError("此游戏分支未审核 ESL 支持，请使用匹配版本的 MOD")
    return [{"source": str(source), "target": f"Data/{tail}"} for source, tail in items]
