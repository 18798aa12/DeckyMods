import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from decky_mods.errors import ModsError
from decky_mods.nexus import NexusClient


@pytest.mark.parametrize("newer_action", ["disconnect", "bind"])
def test_late_bind_cannot_restore_or_replace_newer_account(client, monkeypatch, newer_action):
    nexus, _ = client
    started, release = threading.Event(), threading.Event()

    def validate(url, headers):
        if headers["apikey"] == "slow-key":
            started.set()
            assert release.wait(5)
            return {"user_id": 11, "name": "Older"}
        return {"user_id": 22, "name": "Newer"}

    monkeypatch.setattr(nexus.transport, "json", validate)
    with ThreadPoolExecutor() as executor:
        pending = executor.submit(nexus.bind, "slow-key")
        try:
            assert started.wait(5)
            if newer_action == "disconnect":
                nexus.disconnect()
            else:
                nexus.bind("new-key")
        finally:
            release.set()
        with pytest.raises(ModsError, match="取消|变更"):
            pending.result(timeout=5)
    expected = None if newer_action == "disconnect" else 22
    assert nexus.status()["user_id"] == expected
    assert NexusClient(nexus.directory).status()["user_id"] == expected


@pytest.fixture
def client(tmp_path, monkeypatch):
    client = NexusClient(tmp_path / "nexus")
    calls = []

    def request(url, headers):
        calls.append((url, headers))
        if "validate" in url:
            return {
                "user_id": 42,
                "name": "Tester",
                "is_premium": False,
                "key": "never-public",
                "email": "private@example.invalid",
            }
        if "download_link" in url:
            return [{"URI": "https://cf-files.nexusmods.com/file.zip?token=private"}]
        if "/files.json" in url:
            return {
                "files": [
                    {
                        "file_id": 10,
                        "name": "Main",
                        "version": "1",
                        "category_name": "MAIN",
                        "size_in_bytes": 3,
                        "description": "demo",
                        "is_primary": True,
                    }
                ]
            }
        return {"mod_id": 5, "name": "Demo", "author": "Author", "summary": "Description"}

    monkeypatch.setattr(client.transport, "json", request)
    client.bind("test-key")
    return client, calls


def test_bind_stores_private_key_without_returning_it(client):
    nexus, calls = client
    status = nexus.status()
    assert status == {
        "connected": True,
        "name": "Tester",
        "premium": False,
        "user_id": 42,
        "error": None,
    }
    assert "test-key" not in json.dumps(status)
    saved = nexus.directory / "account.json"
    assert saved.stat().st_mode & 0o777 == 0o600
    assert nexus.directory.stat().st_mode & 0o777 == 0o700
    assert calls[0][1]["apikey"] == "test-key"
    assert calls[0][1]["Application-Name"] == "DeckyMods"
    assert NexusClient(nexus.directory).status()["user_id"] == 42
    assert nexus.disconnect()["connected"] is False
    assert not saved.exists()


@pytest.mark.parametrize(
    "ref",
    [
        "5",
        "https://www.nexusmods.com/stellarblade/mods/5",
        "https://www.nexusmods.com/games/stellarblade/mods/5?tab=files",
    ],
)
def test_resolve_legacy_modern_and_number(client, ref):
    nexus, _ = client
    mod = nexus.resolve("stellarblade", ref)
    assert mod["mod_id"] == 5 and mod["files"][0]["file_id"] == 10
    assert mod["files"][0]["size_bytes"] == 3
    assert mod["page_url"] == "https://www.nexusmods.com/stellarblade/mods/5"


def test_resolve_includes_bounded_full_description_and_version(client, monkeypatch):
    nexus, _ = client
    monkeypatch.setattr(
        nexus.transport,
        "json",
        lambda url, headers: {"files": []}
        if url.endswith("/files.json")
        else {"mod_id": 5, "description": "x" * 40000, "version": "v" * 200},
    )
    result = nexus.resolve("stellarblade", "5")
    assert len(result["description"]) == 32768
    assert len(result["version"]) == 128


@pytest.mark.parametrize(
    "ref",
    [
        "https://www.nexusmods.com/skyrim/mods/5",
        "-1",
        "https://evil.test/stellarblade/mods/5",
        "0",
        "http://www.nexusmods.com/stellarblade/mods/5",
        "https://www.nexusmods.com@evil.test/stellarblade/mods/5",
    ],
)
def test_resolve_rejects_wrong_game_and_untrusted_urls(client, ref):
    with pytest.raises(ModsError):
        client[0].resolve("stellarblade", ref)


def grant(**overrides):
    values = {"key": "grant-token", "expires": str(int(time.time()) + 300), "user_id": "42"}
    values.update(overrides)
    return "nxm://stellarblade/mods/5/files/10?" + "&".join(f"{k}={v}" for k, v in values.items())


def test_nxm_identity_and_free_download(client, tmp_path, monkeypatch):
    nexus, calls = client
    parsed = nexus.parse_nxm(grant())
    assert parsed["domain"] == "stellarblade" and parsed["file_id"] == 10
    downloads = []
    monkeypatch.setattr(nexus.transport, "download", lambda *args: downloads.append(args))
    cancel = threading.Event()
    nexus.download(
        "stellarblade", 5, 10, tmp_path / "download", cancel, lambda *_: None, nxm_uri=grant()
    )
    assert downloads and "key=grant-token" in calls[-1][0]
    assert nexus.browser_url("stellarblade", 5, 10).endswith("?tab=files&file_id=10")


@pytest.mark.parametrize(
    "overrides", [{"expires": "1"}, {"user_id": "43"}, {"key": ""}, {"expires": "x"}]
)
def test_rejects_expired_mismatched_grants(client, overrides):
    with pytest.raises(ModsError):
        client[0].parse_nxm(grant(**overrides))


def test_rejects_download_mismatched_identity_and_missing_grant(client, tmp_path):
    nexus, _ = client
    args = ("stellarblade", 5, 10, tmp_path / "d", threading.Event(), lambda *_: None)
    with pytest.raises(ModsError, match="网页"):
        nexus.download(*args)
    with pytest.raises(ModsError):
        nexus.download(*args, nxm_uri=grant().replace("/files/10", "/files/11"))


def test_cancel_before_network(client, tmp_path):
    nexus, calls = client
    cancel = threading.Event()
    cancel.set()
    before = len(calls)
    with pytest.raises(ModsError, match="取消"):
        nexus.download(
            "stellarblade", 5, 10, tmp_path / "d", cancel, lambda *_: None, nxm_uri=grant()
        )
    assert len(calls) == before


def test_credentials_symlink_rejected(tmp_path):
    directory = tmp_path / "nexus"
    directory.mkdir()
    elsewhere = tmp_path / "secret"
    elsewhere.write_text("do not change")
    (directory / "account.json").symlink_to(elsewhere)
    with pytest.raises(ModsError):
        NexusClient(directory)
    assert elsewhere.read_text() == "do not change"


def test_bind_validation_failure_does_not_replace_good_account(client, monkeypatch):
    nexus, _ = client

    def reject(*_):
        raise ModsError("Nexus 登录失效，请重新绑定 API Key")

    monkeypatch.setattr(nexus.transport, "json", reject)
    with pytest.raises(ModsError):
        nexus.bind("wrong-key")
    assert nexus.status()["user_id"] == 42


def test_invalid_api_key_header_injection(client):
    with pytest.raises(ModsError):
        client[0].bind("a\r\nb")
