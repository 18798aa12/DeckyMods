"""Verified TLS trust for system Python and Decky's frozen Python runtime."""

import ssl
from pathlib import Path

from .errors import ModsError

_SYSTEM_BUNDLES = (
    Path("/etc/ssl/cert.pem"),
    Path("/etc/ssl/certs/ca-certificates.crt"),
    Path("/etc/pki/tls/certs/ca-bundle.crt"),
)


def trusted_context() -> ssl.SSLContext:
    """Use OS CA certificates when the frozen runtime has an empty trust store."""
    context = ssl.create_default_context()
    if context.cert_store_stats()["x509_ca"]:
        return context
    for bundle in _SYSTEM_BUNDLES:
        if not bundle.is_file():
            continue
        try:
            context.load_verify_locations(cafile=str(bundle))
        except (OSError, ssl.SSLError):
            continue
        if context.cert_store_stats()["x509_ca"]:
            return context
    raise ModsError("系统 HTTPS 证书库不可用，请检查 SteamOS 系统证书后重试")
