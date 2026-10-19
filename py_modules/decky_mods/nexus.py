"""Official Nexus v1 API integration with browser-generated free-user grants."""

import re
import threading
import time
from collections.abc import Callable
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

from ._nexus_private import private_directory, read_json, write_json
from .errors import ModsError
from .network import SafeTransport

API = "https://api.nexusmods.com/v1"
DOMAIN = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
KEY = re.compile(r"[!-~]{1,4096}\Z")
MOD_PATH = re.compile(r"/(?:games/)?([a-z0-9-]+)/mods/([1-9][0-9]*)/?\Z")
NXM_PATH = re.compile(r"/mods/([1-9][0-9]*)/files/([1-9][0-9]*)\Z")
EMPTY_AUTH = {"connected": False, "name": None, "premium": False, "user_id": None, "error": None}


def _identifier(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ModsError("MOD 或文件编号必须是正整数")
    if not re.fullmatch(r"[1-9][0-9]{0,14}", str(value)):
        raise ModsError("MOD 或文件编号必须是正整数")
    return int(value)


def _domain(value: str) -> str:
    if not isinstance(value, str) or not DOMAIN.fullmatch(value):
        raise ModsError("请选择有效的 Nexus 游戏")
    return value


def _text(value: object, maximum: int = 2048) -> str:
    return value[:maximum] if isinstance(value, str) else ""


class NexusClient:
    """The API key stays in this user's private local directory and API headers."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)
        private_directory(self.directory)
        self.transport = SafeTransport()
        self._lock = threading.RLock()
        self._auth_revision = 0
        saved = read_json(self.directory / "account.json")
        self._account = saved if saved is not None else {}
        if saved is not None and (
            not isinstance(saved.get("key"), str)
            or not KEY.fullmatch(saved["key"])
            or not isinstance(saved.get("auth"), dict)
        ):
            raise ModsError("Nexus 本地设置无效，请重新绑定")

    def status(self) -> dict:
        with self._lock:
            auth = self._account.get("auth", EMPTY_AUTH)
            # Explicit whitelist prevents future response additions leaking credentials.
            return {key: auth.get(key, default) for key, default in EMPTY_AUTH.items()}

    def _headers(self, key: str | None = None) -> dict[str, str]:
        with self._lock:
            credential = key if key is not None else self._account.get("key")
        if not credential:
            raise ModsError("请先绑定 Nexus 个人 API Key，并在网页使用相同账号登录")
        return {
            "apikey": credential,
            "Application-Name": "DeckyMods",
            "Application-Version": "0.2.11",
            "Protocol-Version": "1.0.0",
            "Accept": "application/json",
        }

    def bind(self, key: str) -> dict:
        if not isinstance(key, str) or not KEY.fullmatch(key):
            raise ModsError("请输入有效的个人 API Key，请勿输入密码或网址")
        with self._lock:
            self._auth_revision += 1
            revision = self._auth_revision
        result = self.transport.json(API + "/users/validate.json", self._headers(key))
        if not isinstance(result, dict):
            raise ModsError("Nexus 登录验证返回无效数据")
        user_id = _identifier(result.get("user_id"))
        name = _text(result.get("name"), 120)
        if not name:
            raise ModsError("Nexus 登录验证缺少账号名称")
        auth = {
            "connected": True,
            "name": name,
            "premium": result.get("is_premium") is True,
            "user_id": user_id,
            "error": None,
        }
        account = {"key": key, "auth": auth}
        with self._lock:
            if revision != self._auth_revision:
                raise ModsError("账号操作已变更，这次绑定已取消，请以当前账号状态为准")
            write_json(self.directory / "account.json", account)
            self._account = account
        return {**auth}

    def disconnect(self) -> dict:
        with self._lock:
            self._auth_revision += 1
            try:
                (self.directory / "account.json").unlink(missing_ok=True)
            except OSError:
                raise ModsError("无法删除 Nexus 本地授权文件") from None
            self._account = {}
        return self.status()

    def _reference(self, domain: str, reference: str) -> int:
        _domain(domain)
        if not isinstance(reference, str) or len(reference) > 2048:
            raise ModsError("请输入 Nexus MOD 编号或 MOD 页面网址")
        reference = reference.strip()
        if reference.isascii() and reference.isdecimal():
            return _identifier(reference)
        try:
            parsed = urlsplit(reference)
            match = MOD_PATH.fullmatch(parsed.path)
            if (
                parsed.scheme != "https"
                or parsed.hostname
                not in {"nexusmods.com", "www.nexusmods.com", "next.nexusmods.com"}
                or parsed.username is not None
                or parsed.port not in (None, 443)
                or not match
                or "\\" in reference
                or any(ord(c) < 32 for c in reference)
            ):
                raise ValueError
            if match[1] != domain:
                raise ModsError("这个 MOD 属于其他游戏，请先切换到对应游戏")
            return _identifier(match[2])
        except ValueError:
            raise ModsError("请输入有效的 HTTPS Nexus MOD 页面网址") from None

    def resolve(self, domain: str, reference: str) -> dict:
        mod_id = self._reference(domain, reference)
        base = f"{API}/games/{domain}/mods/{mod_id}"
        info = self.transport.json(base + ".json", self._headers())
        files = self.transport.json(base + "/files.json", self._headers())
        if (
            not isinstance(info, dict)
            or not isinstance(files, dict)
            or not isinstance(files.get("files"), list)
        ):
            raise ModsError("Nexus MOD 信息格式无效")
        if info.get("mod_id", mod_id) != mod_id:
            raise ModsError("Nexus 返回的 MOD 编号不匹配")
        choices = []
        for item in files["files"][:2000]:
            if not isinstance(item, dict):
                raise ModsError("Nexus 文件信息格式无效")
            # Archived/deleted files cannot be downloaded normally.
            if item.get("category_id") in (6, 7) or item.get("category_name") in {
                "DELETED",
                "ARCHIVED",
            }:
                continue
            raw_size = item.get("size_in_bytes")
            size = raw_size if isinstance(raw_size, int) and not isinstance(raw_size, bool) else 0
            choices.append(
                {
                    "file_id": _identifier(item.get("file_id")),
                    "name": _text(item.get("name"), 256),
                    "version": _text(item.get("version"), 128),
                    "category": _text(item.get("category_name"), 128),
                    "size_bytes": max(0, size),
                    "description": _text(item.get("description"), 8192),
                    "primary": item.get("is_primary") is True,
                }
            )
        return {
            "mod_id": mod_id,
            "name": _text(info.get("name"), 256),
            "author": _text(info.get("author"), 256),
            "summary": _text(info.get("summary")),
            "description": _text(info.get("description"), 32768),
            "version": _text(info.get("version"), 128),
            "page_url": f"https://www.nexusmods.com/{domain}/mods/{mod_id}",
            "files": choices,
        }

    def browser_url(self, domain: str, mod_id: int, file_id: int) -> str:
        return (
            f"https://www.nexusmods.com/{_domain(domain)}/mods/{_identifier(mod_id)}"
            f"?tab=files&file_id={_identifier(file_id)}"
        )

    def parse_nxm(self, uri: str) -> dict:
        if not self.status()["connected"]:
            raise ModsError("请先绑定 Nexus 账号，再重新点击网页下载")
        try:
            if (
                not isinstance(uri, str)
                or len(uri) > 8192
                or any(ord(c) < 32 for c in uri)
                or "\\" in uri
            ):
                raise ValueError
            parsed = urlsplit(uri)
            match = NXM_PATH.fullmatch(parsed.path)
            query = parse_qs(parsed.query, strict_parsing=True, max_num_fields=8)
            if (
                parsed.scheme != "nxm"
                or not match
                or parsed.username is not None
                or parsed.port is not None
                or parsed.fragment
                or any(len(values) != 1 for values in query.values())
            ):
                raise ValueError
            domain = _domain(parsed.hostname or "")
            key = query["key"][0]
            expires = int(query["expires"][0])
            user_id = _identifier(query["user_id"][0])
            if not re.fullmatch(r"[A-Za-z0-9_+=./-]{1,4096}", key):
                raise ValueError
            if expires <= int(time.time()):
                raise ModsError("Nexus 网页下载授权已过期，请重新点击 Download with Manager")
            if user_id != self.status()["user_id"]:
                raise ModsError("网页登录的 Nexus 账号与插件绑定账号不同，请使用同一个账号")
            return {
                "domain": domain,
                "mod_id": _identifier(match[1]),
                "file_id": _identifier(match[2]),
                "user_id": user_id,
                "key": key,
                "expires": expires,
            }
        except (ValueError, KeyError, TypeError):
            raise ModsError("NXM 下载授权格式无效，请重新在 Nexus 网页确认下载") from None

    def download(
        self,
        domain: str,
        mod_id: int,
        file_id: int,
        destination: Path,
        cancel: threading.Event,
        progress: Callable[[int, int], None],
        nxm_uri: str | None = None,
    ) -> None:
        if cancel.is_set():
            raise ModsError("下载已取消")
        _domain(domain)
        mod_id, file_id = _identifier(mod_id), _identifier(file_id)
        query = ""
        if nxm_uri is not None:
            grant = self.parse_nxm(nxm_uri)
            if (grant["domain"], grant["mod_id"], grant["file_id"]) != (domain, mod_id, file_id):
                raise ModsError("网页授权的游戏、MOD 或文件与当前下载不一致")
            query = "?" + urlencode({"key": grant["key"], "expires": grant["expires"]})
        elif not self.status()["premium"]:
            raise ModsError(
                "普通会员请先在 Nexus 网页登录并点击 Download with Manager；"
                "也可手动下载后导入压缩包"
            )
        url = f"{API}/games/{domain}/mods/{mod_id}/files/{file_id}/download_link.json{query}"
        links = self.transport.json(url, self._headers())
        if (
            not isinstance(links, list)
            or not links
            or not isinstance(links[0], dict)
            or not isinstance(links[0].get("URI"), str)
        ):
            raise ModsError("Nexus 没有返回可用下载地址，请重新在网页确认下载")
        if cancel.is_set():
            raise ModsError("下载已取消")
        self.transport.download(links[0]["URI"], destination, cancel, progress)
