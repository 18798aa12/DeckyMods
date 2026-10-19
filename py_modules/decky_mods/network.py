"""Bounded HTTPS transport; DNS is checked once and pinned to the TLS connection."""

import http.client
import ipaddress
import json
import os
import socket
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path
from types import TracebackType
from urllib.parse import SplitResult, urljoin, urlsplit

from .dns_fallback import resolve_public
from .errors import ModsError
from .tls import trusted_context

API_HOST = "api.nexusmods.com"
MAX_DOWNLOAD = 8 * 1024**3
MAX_JSON = 8 * 1024**2
REDIRECTS = {301, 302, 303, 307, 308}
BASE_HEADERS = {"User-Agent": "DeckyMods/0.3.0", "Accept-Encoding": "identity"}


def validate_url(url: str, *, api: bool) -> SplitResult:
    try:
        if not isinstance(url, str) or len(url) > 16384 or any(ord(c) < 32 for c in url):
            raise ValueError
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        allowed = (
            host == API_HOST
            if api
            else any(
                host == suffix or host.endswith("." + suffix)
                for suffix in ("nexusmods.com", "nexus-cdn.com")
            )
        )
        if (
            parsed.scheme != "https"
            or parsed.port not in (None, 443)
            or not allowed
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or "\\" in url
        ):
            raise ValueError
        return parsed
    except (ValueError, TypeError):
        raise ModsError("Nexus 返回了不受信任的下载地址，已阻止请求") from None


def public_addresses(host: str) -> list[tuple]:
    try:
        results = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        addresses = [ipaddress.ip_address(item[4][0]) for item in results]
        virtual = ipaddress.ip_network("198.18.0.0/15")
        if addresses and all(address.version == 4 and address in virtual for address in addresses):
            results = resolve_public(host)
            addresses = [ipaddress.ip_address(item[4][0]) for item in results]
        if not results or any(
            not address.is_global or address.is_multicast or address.is_reserved
            for address in addresses
        ):
            raise ModsError("Nexus 域名解析到了非公网地址，已阻止请求")
        return results
    except (OSError, ValueError):
        raise ModsError("无法解析 Nexus 域名，请检查网络") from None


class _PinnedHTTPS(http.client.HTTPSConnection):
    def connect(self) -> None:
        addresses = public_addresses(self.host)
        last_error: OSError | None = None
        for family, socktype, protocol, _, address in addresses:
            connection = socket.socket(family, socktype, protocol)
            connection.settimeout(self.timeout)
            try:
                connection.connect(address)
                self.sock = self._context.wrap_socket(connection, server_hostname=self.host)
                return
            except OSError as error:
                connection.close()
                last_error = error
        if last_error:
            raise last_error
        raise OSError("No public addresses")


def _status_error(status: int) -> None:
    messages = {
        401: "Nexus 登录失效，请重新绑定 API Key",
        403: "Nexus 拒绝访问：请检查账号权限，普通会员请重新在网页确认下载",
        404: "Nexus MOD 或文件不存在，可能已被作者删除",
        429: "Nexus 请求过于频繁，请稍后重试",
    }
    if status != 200:
        raise ModsError(messages.get(status, "Nexus 服务暂时不可用，请稍后重试"))


class _OwnedResponse:
    """Keep a persistent HTTP connection alive until its response is consumed."""

    def __init__(
        self, response: http.client.HTTPResponse, connection: http.client.HTTPConnection
    ) -> None:
        self._response = response
        self._connection = connection
        self._closed = False

    @property
    def status(self) -> int:
        return self._response.status

    def getheader(self, name: str, default: str | None = None) -> str | None:
        return self._response.getheader(name, default)

    def read(self, amount: int | None = None) -> bytes:
        return self._response.read(amount)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            try:
                self._response.close()
            finally:
                self._connection.close()

    def __enter__(self) -> "_OwnedResponse":
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class SafeTransport:
    """No proxy environment, cookies, referer, redirects with API credentials, or URL logging."""

    def _once(self, url: str, headers: dict[str, str]) -> _OwnedResponse:
        parsed = urlsplit(url)
        connection = _PinnedHTTPS(parsed.hostname, timeout=20, context=trusted_context())
        try:
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            connection.request("GET", path, headers=headers)
            return _OwnedResponse(connection.getresponse(), connection)
        except (OSError, http.client.HTTPException, ValueError):
            connection.close()
            raise ModsError("连接 Nexus 失败，请检查网络后重试") from None
        except BaseException:
            connection.close()
            raise

    def _open(self, url: str, headers: dict[str, str], *, api: bool) -> _OwnedResponse:
        for _ in range(6):
            validate_url(url, api=api)
            response = self._once(url, headers)
            if response.status in REDIRECTS:
                location = response.getheader("Location")
                response.close()
                # API endpoints should not redirect; never forward an API key.
                if api or not location:
                    raise ModsError("Nexus 返回了异常跳转，已阻止请求")
                url = urljoin(url, location)
                continue
            try:
                _status_error(response.status)
            except ModsError:
                response.close()
                raise
            return response
        raise ModsError("Nexus 下载跳转次数过多")

    def json(self, url: str, headers: dict[str, str]) -> dict | list:
        with self._open(url, {**BASE_HEADERS, **headers}, api=True) as response:
            try:
                length = response.getheader("Content-Length")
                if length is not None:
                    length = length.strip(" \t")
                if length is not None and (
                    not length.isascii() or not length.isdecimal() or int(length) > MAX_JSON
                ):
                    raise ModsError("Nexus 返回的数据长度无效或过大")
                raw = response.read(MAX_JSON + 1)
                if len(raw) > MAX_JSON:
                    raise ModsError("Nexus 返回的数据过大")
                if length is not None and len(raw) != int(length):
                    raise ValueError("Incomplete response")
                result = json.loads(raw)
                if not isinstance(result, (dict, list)):
                    raise ValueError
                return result
            except (OSError, ValueError, http.client.HTTPException):
                raise ModsError("Nexus 返回的数据无效或连接中断") from None

    def download(
        self,
        url: str,
        destination: Path,
        cancel: threading.Event,
        progress: Callable[[int, int], None],
        max_bytes: int = MAX_DOWNLOAD,
    ) -> None:
        if cancel.is_set():
            raise ModsError("下载已取消")
        temporary: Path | None = None
        try:
            with self._open(url, BASE_HEADERS, api=False) as response:
                length = response.getheader("Content-Length")
                total = int(length) if length is not None else 0
                if total < 0 or total > max_bytes:
                    raise ModsError("MOD 文件超过下载大小限制")
                if destination.exists() or destination.is_symlink():
                    raise ModsError("下载目标已存在，请重新开始下载")
                fd, name = tempfile.mkstemp(prefix=".download-", dir=destination.parent)
                temporary = Path(name)
                done = 0
                with os.fdopen(fd, "wb") as output:
                    progress(0, total)
                    while True:
                        if cancel.is_set():
                            raise ModsError("下载已取消")
                        chunk = response.read(256 * 1024)
                        if not chunk:
                            break
                        done += len(chunk)
                        if done > max_bytes or (total and done > total):
                            raise ModsError("MOD 文件超过下载大小限制")
                        output.write(chunk)
                        progress(done, total)
                    if total and done != total:
                        raise ModsError("MOD 下载不完整，请重新下载")
                    if not done:
                        raise ModsError("MOD 下载为空，请重新下载")
                    output.flush()
                    os.fsync(output.fileno())
                if cancel.is_set():
                    raise ModsError("下载已取消")
                # Hard link publishes atomically without replacing an existing destination.
                os.link(temporary, destination)
        except (OSError, ValueError, http.client.HTTPException):
            raise ModsError("MOD 下载失败或磁盘空间不足，请重试") from None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
