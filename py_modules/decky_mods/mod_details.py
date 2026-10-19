"""Bounded local MOD notes and lazy, official Nexus description retrieval."""

import configparser
import html
import json
import os
import re
import stat
import threading
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from ._nexus_private import read_json
from .errors import ModsError
from .nexus import DOMAIN, MOD_PATH, NexusClient
from .paths import atomic_write, private_directory

_LIMIT = 32768
_MOD_ID = re.compile(r"[a-f0-9]{32}\Z")
_BBCODE = re.compile(
    r"\[/?(?:b|i|u|s|size|color|font|url|quote|code|list|\*|spoiler|center|left|right|heading)"
    r"(?:=[^\]\r\n]{0,2048})?\]",
    re.IGNORECASE,
)
_FIELDS = ("name", "description", "author", "version")


class _PlainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "iframe", "svg"}:
            self.hidden += 1
        elif tag in {"p", "br", "div", "li", "h1", "h2", "h3"} and not self.hidden:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "iframe", "svg"} and self.hidden:
            self.hidden -= 1
        elif tag in {"p", "div", "li", "h1", "h2", "h3"} and not self.hidden:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def _plain(value: object, limit: int = _LIMIT) -> str:
    if not isinstance(value, str):
        return ""
    value = html.unescape(value[: _LIMIT * 2])
    value = re.sub(r"\[img(?:=[^\]]*)?\].*?\[/img\]", "", value, flags=re.I | re.S)
    parser = _PlainText()
    parser.feed(value)
    value = _BBCODE.sub("", "".join(parser.parts))
    value = "".join(
        char
        for char in value
        if char in "\n\t"
        or (
            ord(char) >= 32
            and ord(char) != 127
            and char not in "\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069"
        )
    )
    return re.sub(r"\n{3,}", "\n\n", value).strip()[:limit]


def _number(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    return int(value) if re.fullmatch(r"[1-9][0-9]{0,14}", str(value)) else None


def _reference(value: object, domain: str) -> int | None:
    if not isinstance(value, str) or len(value) > 2048:
        return None
    try:
        parsed = urlsplit(value)
        match = MOD_PATH.fullmatch(parsed.path)
        if (
            parsed.scheme == "https"
            and parsed.hostname in {"nexusmods.com", "www.nexusmods.com", "next.nexusmods.com"}
            and parsed.username is None
            and parsed.password is None
            and parsed.port in (None, 443)
            and match
            and match[1] == domain
            and "\\" not in value
            and not any(ord(char) < 32 for char in value)
        ):
            return _number(match[2])
    except ValueError:
        return None
    return None


def _read_note(root: Path, relative: Path) -> str:
    """Open each directory without following links, including intermediate paths."""
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in relative.parts[:-1]:
            next_descriptor = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor
            )
            os.close(descriptor)
            descriptor = next_descriptor
        file_descriptor = os.open(
            relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor
        )
        with os.fdopen(file_descriptor, "rb") as source:
            info = os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > _LIMIT:
                raise ModsError("档案说明文件过大或类型不安全，未读取")
            contents = source.read(_LIMIT + 1)
            if len(contents) > _LIMIT:
                raise ModsError("档案说明文件过大，未读取")
            return contents.decode("utf-8-sig", errors="replace")
    finally:
        os.close(descriptor)


def _notes(root: Path) -> tuple[list[Path], bool]:
    found: list[Path] = []
    visited = 0
    for directory, children, files in os.walk(root, followlinks=False):
        relative = Path(directory).relative_to(root)
        children[:] = sorted(
            child
            for child in children
            if not child.startswith(".")
            and not (Path(directory) / child).is_symlink()
            and len(relative.parts) < 8
        )
        visited += len(children) + len(files)
        if visited > 10000:
            return found, True
        for name in sorted(files):
            if name.casefold() in {"modinfo.ini", "readme", "readme.txt", "readme.md"}:
                found.append(relative / name)
                if len(found) > 32:
                    return found[:32], True
    return sorted(found, key=lambda path: (len(path.parts), str(path))), False


class ModDetails:
    def __init__(self, directory: Path, nexus: NexusClient) -> None:
        self.directory = Path(directory)
        private_directory(self.directory)
        self.nexus = nexus
        self._lock = threading.RLock()

    def capture(
        self, extracted: Path, identity: dict | None, archive_name: str, game: dict
    ) -> dict | None:
        """Read optional archive notes during staging; never contact any server."""
        metadata = {
            "game_id": game["id"],
            "nexus_domain": game["nexus_domain"],
            "archive_name": _plain(Path(archive_name).name, 256),
            "reference_id": _number((identity or {}).get("mod_id")),
        }
        paths, truncated = _notes(extracted)
        warning = "档案说明文件数量较多，仅检查了有界范围" if truncated else None
        ini = [path for path in paths if path.name.casefold() == "modinfo.ini"]
        if len(ini) > 1:
            warning = "压缩包有多个 modinfo.ini，未猜测使用哪个 MOD 的信息"
        elif ini:
            try:
                text = _read_note(extracted, ini[0])
                parser = configparser.ConfigParser(interpolation=None)
                parser.read_string(text if text.lstrip().startswith("[") else "[mod]\n" + text)
                sections = [parser[section] for section in parser.sections()]
                if len(sections) != 1:
                    raise ValueError("ambiguous metadata")
                section = sections[0]
                metadata = {
                    **metadata,
                    **{
                        key: _plain(section.get(key), 512 if key != "description" else _LIMIT)
                        for key in _FIELDS
                    },
                }
                if not metadata["reference_id"]:
                    metadata = {
                        **metadata,
                        "reference_id": next(
                            (
                                reference
                                for key in ("homepage", "website", "url", "nexus")
                                if (reference := _reference(section.get(key), game["nexus_domain"]))
                            ),
                            None,
                        ),
                    }
            except (OSError, ValueError, configparser.Error, ModsError):
                warning = "档案 modinfo.ini 无法安全读取，已保留 MOD 文件安装流程"
        if not metadata.get("description"):
            readmes = [path for path in paths if path.name.casefold() != "modinfo.ini"]
            if readmes:
                try:
                    metadata = {
                        **metadata,
                        "description": _plain(_read_note(extracted, readmes[0])),
                    }
                except (OSError, ModsError):
                    warning = "档案说明文件无法安全读取，已保留 MOD 文件安装流程"
        if warning:
            metadata = {**metadata, "warning": warning}
        return (
            metadata
            if any(metadata.get(key) for key in (*_FIELDS, "reference_id", "warning"))
            else None
        )

    def _path(self, mod_id: str) -> Path:
        if not isinstance(mod_id, str) or not _MOD_ID.fullmatch(mod_id):
            raise ModsError("MOD 记录编号无效")
        return self.directory / f"{mod_id}.json"

    def remember(self, mod_id: str, metadata: dict | None) -> None:
        path = self._path(mod_id)
        if metadata is None:
            return
        if not isinstance(metadata, dict):
            raise ModsError("MOD 说明信息无效")
        value = {
            **{
                key: _plain(metadata.get(key), _LIMIT if key == "description" else 512)
                for key in (*_FIELDS, "game_id", "nexus_domain", "archive_name", "warning")
            },
            "reference_id": _number(metadata.get("reference_id")),
        }
        with self._lock:
            atomic_write(path, json.dumps(value, ensure_ascii=False).encode("utf-8"))

    def get(self, game: dict, mod: dict) -> dict:
        """Called on expansion only; optional description failures never alter MODs."""
        error = None
        local: dict = {}
        try:
            embedded = mod.get("details")
            if embedded is not None:
                if not isinstance(embedded, dict):
                    raise ModsError("本地 MOD 说明格式无效")
                saved = embedded
            else:
                with self._lock:
                    saved = read_json(self._path(mod["id"]), limit=256 * 1024)
            if saved:
                if (
                    saved.get("game_id") != game["id"]
                    or saved.get("nexus_domain") != game["nexus_domain"]
                ):
                    raise ModsError("本地 MOD 说明属于其他游戏，未使用")
                local = saved
        except ModsError:
            error = "本地 MOD 说明无法安全读取；游戏文件和 MOD 启用状态未改变"
        domain = game.get("nexus_domain")
        valid_domain = isinstance(domain, str) and DOMAIN.fullmatch(domain)
        reference = (
            (
                _number(mod.get("nexus_mod_id"))
                or (_reference(mod.get("source_url"), domain) if valid_domain else None)
                or _number(local.get("reference_id"))
            )
            if valid_domain
            else None
        )
        page_url = f"https://www.nexusmods.com/{domain}/mods/{reference}" if reference else None
        result = {
            "mod_id": mod["id"],
            "name": _plain(local.get("name") or mod.get("name"), 512),
            "description": _plain(local.get("description")),
            "summary": "",
            "author": _plain(local.get("author"), 512),
            "version": _plain(local.get("version"), 512),
            "page_url": page_url,
            "source_url": page_url,
            "origin": "local" if any(local.get(key) for key in _FIELDS) else "unavailable",
            "error": error or _plain(local.get("warning"), 512) or None,
        }
        if reference:
            try:
                info = self.nexus.resolve(domain, str(reference))
                if not isinstance(info, dict) or _number(info.get("mod_id")) != reference:
                    raise ModsError("Nexus 返回的 MOD 编号不匹配，已保留本地说明")
                result = {
                    **result,
                    "name": _plain(info.get("name"), 512) or result["name"],
                    "description": _plain(info.get("description") or info.get("summary"))
                    or result["description"],
                    "summary": _plain(info.get("summary"), 2048),
                    "author": _plain(info.get("author"), 512) or result["author"],
                    "version": _plain(info.get("version"), 512) or result["version"],
                    "origin": "nexus",
                    "error": None,
                }
            except ModsError as exc:
                result = {**result, "error": _plain(str(exc), 512)}
            except (OSError, ValueError, TypeError, KeyError):
                result = {**result, "error": "Nexus 描述暂时无法读取，已保留本地说明"}
        return result
