import http.client
import json
import socket
import ssl

import pytest
from decky_mods.dns_fallback import resolve_public
from decky_mods.errors import ModsError

HOST = "api.nexusmods.com"


def answer(host=HOST, addresses=None):
    return {
        "Status": 0,
        "TC": False,
        "Question": [{"name": host + ".", "type": 1}],
        "Answer": [
            {"name": host + ".", "type": 1, "TTL": 300, "data": address}
            for address in (addresses or ["104.18.24.207"])
        ],
    }


class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.status = status
        self.headers = headers or {}
        self.closed = False
        self.read_limit = None

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def read(self, limit):
        self.read_limit = limit
        return self.body[:limit]

    def close(self):
        self.closed = True


@pytest.fixture
def resolver(monkeypatch):
    calls = []
    response = Response(answer())

    class Connection:
        def __init__(self, host, *, timeout, context):
            self.closed = False
            self.response = response
            self.constructor = (host, timeout, context)
            self.request_values = None
            calls.append(self)

        def request(self, method, target, *, headers):
            self.request_values = (method, target, headers)

        def getresponse(self):
            return self.response

        def close(self):
            self.closed = True

    monkeypatch.setattr(http.client, "HTTPSConnection", Connection)
    return calls, response


def test_fixed_tls_endpoint_and_no_credentials_or_proxy(resolver, monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://user:secret@127.0.0.1:9999")
    calls, response = resolver
    result = resolve_public(HOST)
    assert result == [
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("104.18.24.207", 443))
    ]
    connection = calls[0]
    host, timeout, context = connection.constructor
    assert host == "1.1.1.1"
    assert timeout == 10
    assert context.check_hostname is True
    assert context.verify_mode == ssl.CERT_REQUIRED
    method, target, headers = connection.request_values
    assert method == "GET"
    assert target == "/dns-query?name=api.nexusmods.com&type=A"
    assert headers == {"Accept": "application/dns-json", "Accept-Encoding": "identity"}
    assert response.read_limit == 65537
    assert response.closed
    assert connection.closed


@pytest.mark.parametrize(
    "host",
    [
        "github.com",
        "release-assets.githubusercontent.com",
        "objects.githubusercontent.com",
        "cf-files.nexusmods.com",
        "files.nexus-cdn.com",
        "nexusmods.com",
    ],
)
def test_official_hosts_allowed(resolver, host):
    resolver[1].body = json.dumps(answer(host)).encode()
    assert resolve_public(host)


@pytest.mark.parametrize(
    "host",
    [
        "localhost",
        "127.0.0.1",
        "198.18.0.1",
        "evil.test",
        "nexusmods.com.evil.test",
        "api.nexusmods.com/secret",
        "user@api.nexusmods.com",
        "api.nexusmods.com:443",
        "api.nexusmods.com\r\nX: secret",
        "-bad.nexusmods.com",
        "bad..nexusmods.com",
        None,
    ],
)
def test_untrusted_host_rejected_before_network(resolver, host):
    with pytest.raises(ModsError):
        resolve_public(host)
    assert resolver[0] == []


@pytest.mark.parametrize("status", [301, 302, 307, 403, 500])
def test_redirects_and_http_errors_rejected(resolver, status):
    resolver[1].status = status
    resolver[1].headers["Location"] = "https://evil.test/"
    with pytest.raises(ModsError):
        resolve_public(HOST)
    assert len(resolver[0]) == 1
    assert resolver[1].closed
    assert resolver[0][0].closed


@pytest.mark.parametrize(
    "headers",
    [
        {"Content-Encoding": "gzip"},
        {"Content-Length": "65537"},
        {"Content-Length": "-1"},
        {"Content-Length": "invalid"},
        {"Content-Length": "1"},
    ],
)
def test_bounded_identity_body(resolver, headers):
    resolver[1].headers = headers
    with pytest.raises(ModsError):
        resolve_public(HOST)
    assert resolver[0][0].closed


def test_oversized_actual_body_rejected(resolver):
    resolver[1].body = b" " * 65537
    with pytest.raises(ModsError):
        resolve_public(HOST)


@pytest.mark.parametrize(
    "body",
    [
        b"broken",
        b"[]",
        b"null",
        b'{"Status":0,"Status":3}',
        {**answer(), "Status": 3},
        {**answer(), "Status": False},
        {**answer(), "TC": True},
        {**answer(), "Question": []},
        {**answer(), "Question": [{"name": "evil.test.", "type": 1}]},
        {**answer(), "Question": [{"name": HOST + ".", "type": 28}]},
        {**answer(), "Question": [{"name": HOST + ".", "type": True}]},
        {**answer(), "Answer": "bad"},
    ],
)
def test_response_identity_and_json_structure_checked(resolver, body):
    resolver[1].body = body if isinstance(body, bytes) else json.dumps(body).encode()
    with pytest.raises(ModsError):
        resolve_public(HOST)


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.1",
        "192.168.1.13",
        "169.254.169.254",
        "198.18.0.1",
        "224.0.0.1",
        "0.0.0.0",
        "255.255.255.255",
        "192.0.2.1",
        "2606:4700::1111",
        "bad",
    ],
)
def test_every_a_address_must_be_public_ipv4(resolver, address):
    resolver[1].body = json.dumps(answer(addresses=["104.18.24.207", address])).encode()
    with pytest.raises(ModsError):
        resolve_public(HOST)


def test_no_ipv4_answer_clear_error(resolver):
    body = answer()
    body["Answer"] = [{"name": HOST + ".", "type": 28, "data": "2606:4700::1111"}]
    resolver[1].body = json.dumps(body).encode()
    with pytest.raises(ModsError, match="IPv4"):
        resolve_public(HOST)


def test_cname_chain_and_duplicate_addresses(resolver):
    body = answer()
    body["Answer"] = [
        {"name": HOST + ".", "type": 5, "data": "target.cloudflare.net."},
        {"name": "target.cloudflare.net.", "type": 1, "data": "104.18.24.207"},
        {"name": "target.cloudflare.net.", "type": 1, "data": "104.18.24.207"},
    ]
    resolver[1].body = json.dumps(body).encode()
    assert len(resolve_public(HOST)) == 1


def test_unrelated_a_record_rejected(resolver):
    body = answer()
    body["Answer"][0]["name"] = "unrelated.test."
    resolver[1].body = json.dumps(body).encode()
    with pytest.raises(ModsError):
        resolve_public(HOST)


def test_connection_failure_does_not_echo_raw_error(resolver, monkeypatch):
    def fail(*_, **__):
        raise OSError("sensitive transport diagnostic")

    monkeypatch.setattr(http.client, "HTTPSConnection", fail)
    with pytest.raises(ModsError) as error:
        resolve_public(HOST)
    assert "sensitive transport" not in str(error.value)


@pytest.mark.parametrize("value", [True, None, 1746012367, ["104.18.24.207"]])
def test_ipv4_rdata_must_be_dns_text(resolver, value):
    body = answer()
    body["Answer"][0]["data"] = value
    resolver[1].body = json.dumps(body).encode()
    with pytest.raises(ModsError):
        resolve_public(HOST)


def test_cname_cycle_rejected(resolver):
    body = answer()
    body["Answer"] += [
        {"name": HOST + ".", "type": 5, "data": "target.example."},
        {"name": "target.example.", "type": 5, "data": HOST + "."},
    ]
    resolver[1].body = json.dumps(body).encode()
    with pytest.raises(ModsError):
        resolve_public(HOST)
