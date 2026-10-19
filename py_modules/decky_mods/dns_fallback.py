"""Public IPv4 resolution for official services behind a fake-IP DNS proxy.

Call only after the system resolver returns exclusively 198.18.0.0/15 addresses.
The resolver receives the hostname alone; MOD grants and API keys never enter
this request. Result addresses remain pinned by the normal HTTPS transport.
"""

import http.client
import ipaddress
import json
import re
import socket
import ssl
from urllib.parse import urlencode

from .errors import ModsError

_MAX_RESPONSE = 64 * 1024
_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
_GITHUB = {"github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}
_NEXUS = ("nexusmods.com", "nexus-cdn.com")


def _dns_name(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid DNS name")
    name = value.removesuffix(".").lower()
    if not name or len(name) > 253 or any(not _LABEL.fullmatch(part) for part in name.split(".")):
        raise ValueError("Invalid DNS name")
    return name


def _host(value: object) -> str:
    name = _dns_name(value)
    if name not in _GITHUB and not any(
        name == suffix or name.endswith("." + suffix) for suffix in _NEXUS
    ):
        raise ValueError("Untrusted hostname")
    return name


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _addresses(body: bytes, host: str) -> list[tuple]:
    data = json.loads(body, object_pairs_hook=_unique_object)
    if (
        not isinstance(data, dict)
        or type(data.get("Status")) is not int
        or data["Status"] != 0
        or data.get("TC", False) is not False
    ):
        raise ValueError("Invalid DNS status")
    questions = data.get("Question")
    if not isinstance(questions, list) or len(questions) != 1:
        raise ValueError("Invalid DNS question")
    question = questions[0]
    if (
        not isinstance(question, dict)
        or _dns_name(question.get("name")) != host
        or type(question.get("type")) is not int
        or question["type"] != 1
    ):
        raise ValueError("Mismatched DNS question")
    answers = data.get("Answer", [])
    if not isinstance(answers, list) or len(answers) > 128:
        raise ValueError("Invalid DNS answers")
    aliases: dict[str, str] = {}
    candidates: list[tuple[str, str]] = []
    for record in answers:
        if not isinstance(record, dict) or type(record.get("type")) is not int:
            raise ValueError("Invalid DNS record")
        kind = record["type"]
        if kind not in (1, 5):
            continue
        owner = _dns_name(record.get("name"))
        if kind == 5:
            target = _dns_name(record.get("data"))
            if owner in aliases and aliases[owner] != target:
                raise ValueError("Ambiguous CNAME")
            aliases[owner] = target
        else:
            if not isinstance(record.get("data"), str):
                raise ValueError("Invalid IPv4 answer data")
            address = ipaddress.IPv4Address(record["data"])
            if not address.is_global or address.is_multicast or address.is_reserved:
                raise ValueError("Non-public IPv4 answer")
            candidates.append((owner, str(address)))
    allowed = {host}
    current = host
    while current in aliases:
        current = aliases[current]
        if current in allowed:
            raise ValueError("CNAME cycle")
        allowed.add(current)
    if not candidates:
        raise ModsError("安全 DNS 未返回可用的公网 IPv4 地址，请检查代理或网络")
    if any(owner not in allowed for owner, _ in candidates):
        raise ValueError("Unrelated IPv4 answer")
    addresses = list(dict.fromkeys(address for _, address in candidates))
    return [
        (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (address, 443))
        for address in addresses
    ]


def resolve_public(host: str) -> list[tuple]:
    """Resolve allowlisted service names through fixed TLS-verified Cloudflare DoH."""
    try:
        hostname = _host(host)
    except ValueError:
        raise ModsError("安全 DNS 仅允许查询官方 Nexus 与插件 GitHub 下载域名") from None
    connection: http.client.HTTPSConnection | None = None
    response: http.client.HTTPResponse | None = None
    try:
        connection = http.client.HTTPSConnection(
            "1.1.1.1", timeout=10, context=ssl.create_default_context()
        )
        connection.request(
            "GET",
            "/dns-query?" + urlencode({"name": hostname, "type": "A"}),
            headers={"Accept": "application/dns-json", "Accept-Encoding": "identity"},
        )
        response = connection.getresponse()
        if response.status != 200:
            raise ModsError("安全 DNS 暂不可用，请检查代理或网络后重试")
        if response.getheader("Content-Encoding", "identity") != "identity":
            raise ValueError("Unexpected compressed DNS response")
        length = response.getheader("Content-Length")
        if length is not None and (
            not re.fullmatch(r"[0-9]{1,8}", length) or int(length) > _MAX_RESPONSE
        ):
            raise ValueError("Invalid DNS response size")
        body = response.read(_MAX_RESPONSE + 1)
        if (
            not body
            or len(body) > _MAX_RESPONSE
            or (length is not None and int(length) != len(body))
        ):
            raise ValueError("Invalid DNS response body")
        return _addresses(body, hostname)
    except (OSError, http.client.HTTPException, ValueError, TypeError):
        raise ModsError("无法安全解析公网地址，请检查代理或网络后重试") from None
    finally:
        if response is not None:
            response.close()
        if connection is not None:
            connection.close()
