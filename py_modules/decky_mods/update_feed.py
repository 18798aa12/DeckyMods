"""Bounded, authenticated update feeds and no-root Decky package validation."""

import http.client
import io
import ipaddress
import json
import re
import ssl
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from .errors import ModsError
from .network import _PinnedHTTPS

MAX_MANIFEST = 8192
MAX_PACKAGE = 32 * 1024 * 1024
GITHUB_SOURCE = "https://github.com/18798aa12/DeckyMods/releases/latest/download"
_PRIVATE = tuple(
    ipaddress.ip_network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)
_REDIRECT_HOSTS = {
    "github.com",
    "release-assets.githubusercontent.com",
    "objects.githubusercontent.com",
}
_VERSION = re.compile(r"(?:0|[1-9]\d{0,4})\.(?:0|[1-9]\d{0,4})\.(?:0|[1-9]\d{0,4})")


def version_tuple(value: str) -> tuple[int, int, int]:
    if not isinstance(value, str) or not _VERSION.fullmatch(value):
        raise ModsError("更新版本格式无效")
    values = tuple(int(part) for part in value.split("."))
    return values[0], values[1], values[2]


def validate_source(value: str) -> str | None:
    """Only this project's release feed or literal RFC1918 LAN addresses are allowed."""
    if not isinstance(value, str) or len(value) > 2048 or any(c.isspace() for c in value):
        raise ModsError("更新来源格式无效")
    if not value:
        return None
    normalized = value.rstrip("/")
    if normalized == GITHUB_SOURCE:
        return normalized
    try:
        parsed = urlsplit(normalized)
        address = ipaddress.IPv4Address(parsed.hostname or "")
        if (
            parsed.scheme != "http"
            or not any(address in subnet for subnet in _PRIVATE)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or "\\" in value
            or parsed.port == 0
            or any(ord(c) < 32 for c in value)
        ):
            raise ValueError
        return normalized
    except (ValueError, TypeError):
        raise ModsError("更新来源只支持此项目的 GitHub 发布地址或同一局域网的 HTTP 地址") from None


def fetch(url: str, maximum: int, *, source: str) -> bytes:
    """No environment proxy, auth, cookie, arbitrary redirect or unbounded body."""
    is_github = source == GITHUB_SOURCE
    for _ in range(5):
        parsed = urlsplit(url)
        if is_github:
            if (
                parsed.scheme != "https"
                or parsed.hostname not in _REDIRECT_HOSTS
                or parsed.port not in (None, 443)
                or parsed.username
                or parsed.password
                or parsed.fragment
                or "\\" in url
            ):
                raise ModsError("更新服务器返回了不受信任的跳转")
            connection = _PinnedHTTPS(
                parsed.hostname, timeout=20, context=ssl.create_default_context()
            )
        else:
            if not url.startswith(source + "/") or parsed.query or parsed.fragment:
                raise ModsError("更新服务器地址无效")
            connection = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=20)
        try:
            target = parsed.path or "/"
            if parsed.query:
                target += "?" + parsed.query
            connection.request(
                "GET",
                target,
                headers={"User-Agent": "DeckyMods-Updater/1", "Accept-Encoding": "identity"},
            )
            response = connection.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader("Location")
                response.close()
                if not is_github or not location:
                    raise ModsError("局域网更新来源不允许跳转，请填写直接地址")
                url = urljoin(url, location)
                continue
            if response.status != 200:
                response.close()
                raise ModsError("更新来源暂不可用，请检查来源地址和网络后重试")
            with response:
                length = response.getheader("Content-Length")
                if length is not None and (not length.isdigit() or int(length) > maximum):
                    raise ModsError("更新文件超过大小限制")
                if response.getheader("Content-Encoding", "identity") != "identity":
                    raise ModsError("更新服务器返回了不支持的压缩响应")
                data = response.read(maximum + 1)
                if not data or len(data) > maximum:
                    raise ModsError("更新文件为空或超过大小限制")
                if length is not None and int(length) != len(data):
                    raise ModsError("更新下载不完整，请重新下载")
                return data
        except (OSError, http.client.HTTPException, ValueError):
            raise ModsError("连接更新来源失败，请检查网络后重试") from None
        finally:
            connection.close()
    raise ModsError("更新服务器跳转次数过多")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def json_object(raw: bytes, maximum: int = MAX_MANIFEST) -> dict:
    if len(raw) > maximum:
        raise ModsError("更新数据超过大小限制")
    try:
        parsed = json.loads(raw, object_pairs_hook=_unique_object)
        if not isinstance(parsed, dict):
            raise ValueError
        return parsed
    except (ValueError, UnicodeError):
        raise ModsError("更新数据格式无效") from None


def verified_manifest(raw: bytes, signature: bytes, allowed_signers: Path) -> dict:
    """SSH signatures pin the signing identity independently of LAN/HTTPS transport."""
    if len(raw) > MAX_MANIFEST or len(signature) > MAX_MANIFEST:
        raise ModsError("更新签名或清单超过大小限制")
    if allowed_signers.is_symlink() or not allowed_signers.is_file():
        raise ModsError("插件缺少受信任的更新签名公钥，请重新安装正式包")
    with tempfile.TemporaryDirectory(prefix="deckymods-signature-") as directory:
        signature_path = Path(directory) / "manifest.sig"
        signature_path.write_bytes(signature)
        try:
            result = subprocess.run(
                [
                    "/usr/bin/ssh-keygen",
                    "-Y",
                    "verify",
                    "-f",
                    str(allowed_signers),
                    "-I",
                    "deckymods-release",
                    "-n",
                    "deckymods-update",
                    "-s",
                    str(signature_path),
                ],
                input=raw,
                capture_output=True,
                timeout=10,
                check=False,
            )
            if result.returncode != 0:
                raise ModsError("更新签名验证失败，已拒绝该更新")
        except (OSError, subprocess.SubprocessError):
            raise ModsError("无法验证更新签名，请检查系统 OpenSSH 工具") from None
    manifest = json_object(raw)
    if set(manifest) != {"schema", "version", "filename", "size", "sha256"}:
        raise ModsError("更新清单字段无效")
    if type(manifest["schema"]) is not int or manifest["schema"] != 1:
        raise ModsError("更新清单版本不受支持")
    version_tuple(manifest["version"])
    if manifest["filename"] != f"DeckyMods-v{manifest['version']}.zip":
        raise ModsError("更新文件名无效")
    if type(manifest["size"]) is not int or not 1 <= manifest["size"] <= MAX_PACKAGE:
        raise ModsError("更新文件大小无效")
    if not isinstance(manifest["sha256"], str) or not re.fullmatch(
        r"[0-9a-f]{64}", manifest["sha256"]
    ):
        raise ModsError("更新校验值无效")
    return manifest


def validate_package(data: bytes, manifest: dict, allowed_signers: Path) -> None:
    """Only a complete DeckyMods tree without root flags can reach Decky's installer."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if not entries or len(entries) > 4096:
                raise ValueError
            seen: set[str] = set()
            total = 0
            files: set[str] = set()
            directories: set[str] = set()
            for entry in entries:
                name = entry.filename
                pieces = name.rstrip("/").split("/")
                normalized = name.rstrip("/").casefold()
                mode = stat.S_IFMT(entry.external_attr >> 16)
                parents = {"/".join(pieces[:index]).casefold() for index in range(1, len(pieces))}
                if (
                    pieces[0] != "DeckyMods"
                    or any(part in ("", ".", "..") for part in pieces)
                    or "\\" in name
                    or ":" in name
                    or any(ord(c) < 32 for c in name)
                    or name.rstrip("/").casefold() in seen
                    or entry.flag_bits & 1
                    or mode not in (0, stat.S_IFREG, stat.S_IFDIR)
                    or (mode == stat.S_IFDIR and not entry.is_dir())
                    or entry.orig_filename != name
                    or entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                    or parents & files
                    or (not entry.is_dir() and normalized in directories)
                    or (len(pieces) == 1 and not entry.is_dir())
                    or entry.file_size > 32 * 1024 * 1024
                    or entry.file_size > max(1, entry.compress_size) * 250
                ):
                    raise ValueError
                seen.add(normalized)
                directories.update(parents)
                if entry.is_dir():
                    directories.add(normalized)
                else:
                    files.add(normalized)
                total += entry.file_size
                if total > 128 * 1024 * 1024:
                    raise ValueError
                with archive.open(entry) as stream:
                    consumed = 0
                    while chunk := stream.read(256 * 1024):
                        consumed += len(chunk)
                        if consumed > entry.file_size:
                            raise ValueError
                    if consumed != entry.file_size:
                        raise ValueError
            plugin = json_object(archive.read("DeckyMods/plugin.json"), 65536)
            package = json_object(archive.read("DeckyMods/package.json"), 65536)
            if (
                plugin.get("name") != "DeckyMods"
                or type(plugin.get("api_version")) is not int
                or plugin["api_version"] != 1
                or package.get("remote_binary", []) != []
                or plugin.get("flags") != []
                or package.get("name") != "decky-mods"
                or package.get("version") != manifest["version"]
            ):
                raise ValueError
            for required in ("DeckyMods/main.py", "DeckyMods/dist/index.js"):
                if archive.getinfo(required).file_size == 0:
                    raise ValueError
            # A release signed by the old key must preserve the pinned trust anchor.
            if (
                archive.read("DeckyMods/assets/update-allowed-signers")
                != allowed_signers.read_bytes()
            ):
                raise ValueError
    except (OSError, ValueError, KeyError, RuntimeError, zipfile.BadZipFile, EOFError):
        raise ModsError("更新安装包结构或权限校验失败，已保留当前插件") from None
