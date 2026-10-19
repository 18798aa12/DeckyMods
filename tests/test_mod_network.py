import http.client
import io
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from decky_mods.errors import ModsError
from decky_mods.network import SafeTransport, public_addresses, validate_url


def test_json_bounds_and_parse_errors(monkeypatch):
    import decky_mods.network as network

    transport = SafeTransport()
    monkeypatch.setattr(transport, "_once", lambda *_: Response(b'{"ok": true}'))
    assert transport.json("https://api.nexusmods.com/v1/games.json", {}) == {"ok": True}
    monkeypatch.setattr(transport, "_once", lambda *_: Response(b"<html>private detail</html>"))
    with pytest.raises(ModsError, match="无效"):
        transport.json("https://api.nexusmods.com/v1/games.json", {})
    monkeypatch.setattr(network, "MAX_JSON", 2)
    monkeypatch.setattr(transport, "_once", lambda *_: Response(b"{} "))
    with pytest.raises(ModsError, match="过大"):
        transport.json("https://api.nexusmods.com/v1/games.json", {})


def test_public_dns_error_is_sanitized(monkeypatch):
    def fail(*_args, **_kwargs):
        raise socket.gaierror("private resolver message")

    monkeypatch.setattr(socket, "getaddrinfo", fail)
    with pytest.raises(ModsError, match="解析") as failure:
        public_addresses("api.nexusmods.com")
    assert "private resolver" not in str(failure.value)


def test_pinned_connection_uses_checked_ip_and_original_tls_hostname(monkeypatch):
    import decky_mods.network as network

    calls = []

    class Socket:
        def settimeout(self, timeout):
            calls.append(("timeout", timeout))

        def connect(self, address):
            calls.append(("connect", address))

        def close(self):
            calls.append(("close",))

    class Context:
        check_hostname = False
        verify_mode = 2

        def set_alpn_protocols(self, _):
            pass

        def wrap_socket(self, connection, server_hostname):
            calls.append(("tls", server_hostname))
            return connection

    monkeypatch.setattr(
        network,
        "public_addresses",
        lambda host: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443))],
    )
    monkeypatch.setattr(network.socket, "socket", lambda *_args: Socket())
    connection = network._PinnedHTTPS("api.nexusmods.com", timeout=20, context=Context())
    connection.connect()
    assert ("connect", ("1.1.1.1", 443)) in calls
    assert ("tls", "api.nexusmods.com") in calls
    connection.close()


def test_pinned_connection_closes_failed_socket(monkeypatch):
    import decky_mods.network as network

    closed = []

    class Socket:
        def settimeout(self, _):
            pass

        def connect(self, _):
            raise OSError("private endpoint")

        def close(self):
            closed.append(True)

    monkeypatch.setattr(
        network,
        "public_addresses",
        lambda host: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443))],
    )
    monkeypatch.setattr(network.socket, "socket", lambda *_args: Socket())
    with pytest.raises(OSError):
        network._PinnedHTTPS("api.nexusmods.com").connect()
    assert closed == [True]


def test_once_builds_path_headers_and_keeps_connection_until_response_closed(monkeypatch):
    import decky_mods.network as network

    calls = []

    class Connection:
        def __init__(self, host, **kwargs):
            calls.append(host)

        def request(self, *args, **kwargs):
            calls.append((args, kwargs))

        def getresponse(self):
            return Response(b"{}")

        def close(self):
            calls.append("closed")

    monkeypatch.setattr(network, "_PinnedHTTPS", Connection)
    response = SafeTransport()._once("https://api.nexusmods.com/a?x=y", {"apikey": "demo"})
    assert response.read() == b"{}"
    assert calls[0] == "api.nexusmods.com"
    assert calls[1] == (("GET", "/a?x=y"), {"headers": {"apikey": "demo"}})
    assert "closed" not in calls
    response.close()
    assert calls[-1] == "closed"


def test_once_sanitizes_socket_errors(monkeypatch):
    import decky_mods.network as network

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            raise OSError("sensitive source URL")

        def close(self):
            pass

    monkeypatch.setattr(network, "_PinnedHTTPS", Connection)
    with pytest.raises(ModsError) as failure:
        SafeTransport()._once("https://api.nexusmods.com/a?key=secret", {})
    assert "sensitive" not in str(failure.value) and "secret" not in str(failure.value)


def test_redirect_loop_rejected(tmp_path, monkeypatch):
    transport = SafeTransport()
    monkeypatch.setattr(
        transport, "_once", lambda *_: Response(status=302, headers={"Location": "/loop"})
    )
    with pytest.raises(ModsError, match="跳转次数"):
        transport.download(
            "https://cf-files.nexusmods.com/a", tmp_path / "d", threading.Event(), lambda *_: None
        )


def test_cancel_during_download_removes_partial(tmp_path, monkeypatch):
    transport = SafeTransport()
    monkeypatch.setattr(transport, "_once", lambda *_: Response(b"archive"))
    cancel = threading.Event()

    def progress(done, total):
        if done:
            cancel.set()

    with pytest.raises(ModsError, match="取消"):
        transport.download("https://cf-files.nexusmods.com/a", tmp_path / "d", cancel, progress)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("body,length", [(b"", "0"), (b"abc", "-1"), (b"abc", "bad")])
def test_invalid_lengths_or_empty_rejected(tmp_path, monkeypatch, body, length):
    transport = SafeTransport()
    monkeypatch.setattr(
        transport, "_once", lambda *_: Response(body, headers={"Content-Length": length})
    )
    with pytest.raises(ModsError):
        transport.download(
            "https://cf-files.nexusmods.com/a", tmp_path / "d", threading.Event(), lambda *_: None
        )
    assert list(tmp_path.iterdir()) == []


def test_existing_destination_not_overwritten(tmp_path, monkeypatch):
    transport = SafeTransport()
    monkeypatch.setattr(transport, "_once", lambda *_: Response(b"new"))
    destination = tmp_path / "d"
    destination.write_bytes(b"old")
    with pytest.raises(ModsError):
        transport.download(
            "https://cf-files.nexusmods.com/a", destination, threading.Event(), lambda *_: None
        )
    assert destination.read_bytes() == b"old"


class Response(io.BytesIO):
    def __init__(self, body=b"ok", status=200, headers=None):
        super().__init__(body)
        self.status = status
        self.headers = headers or {}

    def getheader(self, name, default=None):
        return self.headers.get(name, default)


@pytest.mark.parametrize(
    "url",
    [
        "http://cf-files.nexusmods.com/f",
        "https://evil.test/f",
        "https://cf-files.nexusmods.com:444/f",
        "https://127.0.0.1/f",
        "https://a@cf-files.nexusmods.com/f",
        "https://cf-files.nexusmods.com.evil.test/f",
    ],
)
def test_reject_untrusted_cdn(url):
    with pytest.raises(ModsError):
        validate_url(url, api=False)


def test_api_requires_exact_host():
    assert validate_url("https://api.nexusmods.com/v1/users/validate.json", api=True).hostname
    with pytest.raises(ModsError):
        validate_url("https://cf-files.nexusmods.com/f", api=True)


def test_reject_private_or_mixed_dns(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
        ],
    )
    with pytest.raises(ModsError):
        public_addresses("cf-files.nexusmods.com")


def test_reject_multicast_dns(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("224.1.1.1", 443))],
    )
    with pytest.raises(ModsError):
        public_addresses("cf-files.nexusmods.com")


@pytest.mark.parametrize(
    "status,message", [(401, "登录"), (403, "权限"), (404, "不存在"), (429, "频繁"), (500, "服务")]
)
def test_errors_are_sanitized(status, message, monkeypatch):
    transport = SafeTransport()
    monkeypatch.setattr(transport, "_once", lambda *_: Response(b"SECRET", status))
    with pytest.raises(ModsError, match=message) as error:
        transport.json("https://api.nexusmods.com/v1/users/validate.json", {"apikey": "secret"})
    assert "SECRET" not in str(error.value) and "secret" not in str(error.value)


def test_api_redirect_does_not_send_credentials_to_cdn(monkeypatch):
    transport = SafeTransport()
    calls = []

    def request(url, headers):
        calls.append((url, headers))
        return Response(status=302, headers={"Location": "https://cf-files.nexusmods.com/a"})

    monkeypatch.setattr(transport, "_once", request)
    with pytest.raises(ModsError):
        transport.json("https://api.nexusmods.com/a", {"apikey": "secret"})
    assert len(calls) == 1


def test_download_redirect_no_api_headers_and_atomic_private_file(tmp_path, monkeypatch):
    transport = SafeTransport()
    calls = []

    def request(url, headers):
        calls.append((url, headers))
        if len(calls) == 1:
            return Response(
                status=302, headers={"Location": "https://premium-files.nexusmods.com/a"}
            )
        return Response(b"archive", headers={"Content-Length": "7"})

    monkeypatch.setattr(transport, "_once", request)
    destination = tmp_path / "a.zip"
    progress = []
    transport.download(
        "https://cf-files.nexusmods.com/a?key=secret",
        destination,
        threading.Event(),
        lambda *a: progress.append(a),
    )
    assert destination.read_bytes() == b"archive"
    assert destination.stat().st_mode & 0o777 == 0o600
    assert all("apikey" not in headers for _, headers in calls)
    assert progress[-1] == (7, 7)


def test_truncated_or_oversized_download_leaves_no_file(tmp_path, monkeypatch):
    transport = SafeTransport()
    monkeypatch.setattr(
        transport, "_once", lambda *_: Response(b"abc", headers={"Content-Length": "5"})
    )
    with pytest.raises(ModsError):
        transport.download(
            "https://cf-files.nexusmods.com/a", tmp_path / "a", threading.Event(), lambda *_: None
        )
    assert list(tmp_path.iterdir()) == []
    monkeypatch.setattr(transport, "_once", lambda *_: Response(b"abcdef"))
    with pytest.raises(ModsError):
        transport.download(
            "https://cf-files.nexusmods.com/a",
            tmp_path / "a",
            threading.Event(),
            lambda *_: None,
            max_bytes=3,
        )
    assert list(tmp_path.iterdir()) == []


def test_fake_ip_resolves_to_public_ip_before_original_hostname_tls(monkeypatch):
    import decky_mods.network as network

    fake = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("198.18.50.10", 443))]
    actual = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.2", 443))]
    monkeypatch.setattr(socket, "getaddrinfo", lambda *args, **kwargs: fake)
    calls = []
    monkeypatch.setattr(network, "resolve_public", lambda host: calls.append(host) or actual)
    assert public_addresses("api.nexusmods.com") == actual
    assert calls == ["api.nexusmods.com"]


@pytest.mark.parametrize("address", ["127.0.0.1", "192.168.50.10", "10.0.0.1", "169.254.169.254"])
def test_private_dns_never_triggers_doh_fallback(monkeypatch, address):
    import decky_mods.network as network

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))],
    )
    calls = []
    monkeypatch.setattr(network, "resolve_public", lambda host: calls.append(host))
    with pytest.raises(ModsError):
        public_addresses("api.nexusmods.com")
    assert calls == []


def test_mixed_fake_and_private_dns_is_blocked_without_doh(monkeypatch):
    import decky_mods.network as network

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))
            for ip in ["198.18.50.10", "127.0.0.1"]
        ],
    )
    calls = []
    monkeypatch.setattr(network, "resolve_public", lambda host: calls.append(host))
    with pytest.raises(ModsError):
        public_addresses("api.nexusmods.com")
    assert calls == []


@pytest.fixture
def live_keepalive_transport(monkeypatch):
    import decky_mods.network as network

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def handle(self):
            try:
                super().handle()
            except (ConnectionResetError, BrokenPipeError):
                # The client closes unread bodies on rejected statuses/redirects.
                pass

        def do_GET(self):
            status = 200
            headers = {}
            if self.path == "/json":
                body = b'{"ok":true}'
            elif self.path == "/badjson":
                body = b"private invalid response"
            elif self.path == "/forbidden":
                status, body = 403, b"private error response"
            elif self.path == "/truncated":
                body = b"small"
                self.close_connection = True
            elif self.path in ("/redirect", "/api-redirect"):
                status, body = 302, b""
                headers["Location"] = "https://cf-files.nexusmods.com/archive"
            else:
                body = b"archive payload"
            self.send_response(status)
            self.send_header(
                "Content-Length", "20" if self.path == "/truncated" else str(len(body))
            )
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connections = []

    class Connection(http.client.HTTPConnection):
        def __init__(self):
            super().__init__("127.0.0.1", server.server_port, timeout=3)
            self.close_calls = 0
            connections.append(self)

        def close(self):
            self.close_calls += 1
            super().close()

    monkeypatch.setattr(network, "_PinnedHTTPS", lambda *args, **kwargs: Connection())
    try:
        yield SafeTransport(), connections
    finally:
        for connection in connections:
            connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_real_http11_json_response_stays_open_and_cleanup_owned(live_keepalive_transport):
    transport, connections = live_keepalive_transport
    assert transport.json("https://api.nexusmods.com/json", {"apikey": "dummy-test-value"}) == {
        "ok": True
    }
    assert len(connections) == 1
    assert connections[0].sock is None
    assert connections[0].close_calls == 1


def test_real_http11_download_reads_and_closes_socket(live_keepalive_transport, tmp_path):
    transport, connections = live_keepalive_transport
    destination = tmp_path / "archive.zip"
    transport.download(
        "https://cf-files.nexusmods.com/archive",
        destination,
        threading.Event(),
        lambda *_: None,
    )
    assert destination.read_bytes() == b"archive payload"
    assert connections[0].sock is None
    assert connections[0].close_calls == 1


@pytest.mark.parametrize("path", ["badjson", "forbidden", "api-redirect"])
def test_real_http11_error_closes_response_and_connection(live_keepalive_transport, path):
    transport, connections = live_keepalive_transport
    with pytest.raises(ModsError) as error:
        transport.json("https://api.nexusmods.com/" + path, {"apikey": "dummy-test-value"})
    assert "private" not in str(error.value)
    assert "dummy-test-value" not in str(error.value)
    assert all(connection.sock is None for connection in connections)
    assert all(connection.close_calls == 1 for connection in connections)


def test_real_http11_redirect_closes_first_socket_and_download(live_keepalive_transport, tmp_path):
    transport, connections = live_keepalive_transport
    destination = tmp_path / "archive.zip"
    transport.download(
        "https://cf-files.nexusmods.com/redirect",
        destination,
        threading.Event(),
        lambda *_: None,
    )
    assert destination.read_bytes() == b"archive payload"
    assert len(connections) == 2
    assert all(connection.sock is None for connection in connections)
    assert all(connection.close_calls == 1 for connection in connections)


def test_real_http11_cancel_during_download_releases_resources(live_keepalive_transport, tmp_path):
    transport, connections = live_keepalive_transport
    cancelled = threading.Event()

    def progress(done, total):
        if done:
            cancelled.set()

    with pytest.raises(ModsError, match="取消"):
        transport.download(
            "https://cf-files.nexusmods.com/archive",
            tmp_path / "archive.zip",
            cancelled,
            progress,
        )
    assert list(tmp_path.iterdir()) == []
    assert connections[0].sock is None
    assert connections[0].close_calls == 1


def test_real_http11_truncated_download_releases_resources(live_keepalive_transport, tmp_path):
    transport, connections = live_keepalive_transport
    with pytest.raises(ModsError):
        transport.download(
            "https://cf-files.nexusmods.com/truncated",
            tmp_path / "archive.zip",
            threading.Event(),
            lambda *_: None,
        )
    assert list(tmp_path.iterdir()) == []
    assert connections[0].sock is None
    assert connections[0].close_calls == 1


def test_owned_response_double_close_is_safe(monkeypatch):
    import decky_mods.network as network

    closed = []
    response = Response(b"{}")

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            pass

        def getresponse(self):
            return response

        def close(self):
            closed.append(True)

    monkeypatch.setattr(network, "_PinnedHTTPS", Connection)
    owned = SafeTransport()._once("https://api.nexusmods.com/a", {})
    owned.close()
    owned.close()
    assert response.closed
    assert closed == [True]


def test_getresponse_error_closes_connection_without_echo(monkeypatch):
    import decky_mods.network as network

    closed = []

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            pass

        def getresponse(self):
            raise http.client.HTTPException("private credential")

        def close(self):
            closed.append(True)

    monkeypatch.setattr(network, "_PinnedHTTPS", Connection)
    with pytest.raises(ModsError) as error:
        SafeTransport()._once("https://api.nexusmods.com/a?key=secret", {})
    assert closed == [True]
    assert "secret" not in str(error.value)
    assert "private" not in str(error.value)
