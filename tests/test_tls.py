import ssl

import pytest
from decky_mods import tls
from decky_mods.errors import ModsError


class Context:
    check_hostname = True
    verify_mode = ssl.CERT_REQUIRED

    def __init__(self, ca_count=0, failure=False):
        self.ca_count = ca_count
        self.failure = failure
        self.loaded = []

    def cert_store_stats(self):
        return {"x509_ca": self.ca_count}

    def load_verify_locations(self, *, cafile):
        self.loaded.append(cafile)
        if self.failure:
            raise ssl.SSLError("invalid system bundle")
        self.ca_count = 1


def test_existing_default_trust_is_preserved(monkeypatch):
    context = Context(ca_count=5)
    monkeypatch.setattr(ssl, "create_default_context", lambda: context)
    assert tls.trusted_context() is context
    assert context.loaded == []
    assert context.check_hostname is True
    assert context.verify_mode == ssl.CERT_REQUIRED


def test_empty_frozen_trust_loads_system_bundle(tmp_path, monkeypatch):
    bundle = tmp_path / "system-ca.pem"
    bundle.write_text("test bundle")
    context = Context()
    monkeypatch.setattr(ssl, "create_default_context", lambda: context)
    monkeypatch.setattr(tls, "_SYSTEM_BUNDLES", (tmp_path / "missing.pem", bundle))
    assert tls.trusted_context() is context
    assert context.loaded == [str(bundle)]
    assert context.check_hostname is True
    assert context.verify_mode == ssl.CERT_REQUIRED


@pytest.mark.parametrize("available", [False, True])
def test_missing_or_invalid_ca_never_disables_verification(tmp_path, monkeypatch, available):
    bundle = tmp_path / "system-ca.pem"
    if available:
        bundle.write_text("invalid bundle")
    context = Context(failure=True)
    monkeypatch.setattr(ssl, "create_default_context", lambda: context)
    monkeypatch.setattr(tls, "_SYSTEM_BUNDLES", (bundle,))
    with pytest.raises(ModsError, match="证书"):
        tls.trusted_context()
    assert context.check_hostname is True
    assert context.verify_mode == ssl.CERT_REQUIRED


def test_real_empty_default_store_recovers_os_trust(tmp_path, monkeypatch):
    if not any(bundle.is_file() for bundle in tls._SYSTEM_BUNDLES):
        pytest.skip("No supported system CA bundle on this test host")
    empty_file = tmp_path / "empty.pem"
    empty_file.touch()
    empty_directory = tmp_path / "empty-certificates"
    empty_directory.mkdir()
    monkeypatch.setenv("SSL_CERT_FILE", str(empty_file))
    monkeypatch.setenv("SSL_CERT_DIR", str(empty_directory))
    assert ssl.create_default_context().cert_store_stats()["x509_ca"] == 0
    context = tls.trusted_context()
    assert context.cert_store_stats()["x509_ca"] > 0
    assert context.check_hostname is True
    assert context.verify_mode == ssl.CERT_REQUIRED
