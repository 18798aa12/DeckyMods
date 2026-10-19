"""Signed updates never accept an arbitrary executable or replace user settings."""

import hashlib
import io
import json
import os
import subprocess
import zipfile
from pathlib import Path

import pytest
from decky_mods.errors import ModsError
from decky_mods.package_layout import REQUIRED_FILES
from decky_mods.updates import UpdateManager


@pytest.fixture
def signing(tmp_path):
    plugin = tmp_path / "plugin"
    assets = plugin / "assets"
    assets.mkdir(parents=True)
    key = tmp_path / "release-key"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)], check=True)
    public = key.with_suffix(".pub").read_text().split()
    (assets / "update-allowed-signers").write_text(f"deckymods-release {public[0]} {public[1]}\n")
    return plugin, key


def package(version="0.1.3", flags=None, extra=None, metadata=None, api_version=1):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "DeckyMods/plugin.json",
            json.dumps(
                {
                    "name": "DeckyMods",
                    "flags": [] if flags is None else flags,
                    "api_version": api_version,
                }
            ),
        )
        archive.writestr(
            "DeckyMods/package.json",
            json.dumps({"name": "decky-mods", "version": version, **(metadata or {})}),
        )
        archive.writestr("DeckyMods/main.py", "# signed backend\n")
        archive.writestr("DeckyMods/dist/index.js", "// signed frontend\n")
        for name in REQUIRED_FILES - {
            "plugin.json",
            "package.json",
            "main.py",
            "dist/index.js",
            "assets/update-allowed-signers",
        }:
            archive.writestr("DeckyMods/" + name, "# synthetic runtime fixture\n")
        if extra:
            archive.writestr(extra, "not allowed")
    return output.getvalue()


def feed(tmp_path, key, content, version="0.1.3", **overrides):
    manifest = {
        "schema": 1,
        "version": version,
        "filename": f"DeckyMods-v{version}.zip",
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        **overrides,
    }
    raw = json.dumps(manifest, separators=(",", ":")).encode()
    path = tmp_path / "update.json"
    path.write_bytes(raw)
    path.with_suffix(".json.sig").unlink(missing_ok=True)
    subprocess.run(
        ["ssh-keygen", "-Y", "sign", "-f", str(key), "-n", "deckymods-update", str(path)],
        check=True,
        capture_output=True,
    )
    return raw, path.with_suffix(".json.sig").read_bytes()


def manager(tmp_path, signing, monkeypatch, content=None, **overrides):
    plugin, key = signing
    content = package() if content is None else content
    if zipfile.is_zipfile(io.BytesIO(content)):
        output = io.BytesIO(content)
        with zipfile.ZipFile(output, "a") as archive:
            archive.writestr(
                "DeckyMods/assets/update-allowed-signers",
                (plugin / "assets/update-allowed-signers").read_bytes(),
            )
        content = output.getvalue()
    raw, signature = feed(tmp_path, key, content, **overrides)
    payloads = {"update.json": raw, "update.json.sig": signature, "mods.zip": content}
    update = UpdateManager(plugin, tmp_path / "private-updates", "0.1.2")
    update.configure("http://192.168.50.10:8767", True)
    monkeypatch.setattr(update, "_fetch", lambda url, maximum: payloads[url.rsplit("/", 1)[1]])
    return update, payloads


def test_restart_checks_again_when_available_manifest_was_only_in_memory(
    tmp_path, signing, monkeypatch
):
    update, _ = manager(tmp_path, signing, monkeypatch)
    assert update.check()["available"]
    reopened = UpdateManager(signing[0], update.directory, "0.1.2")
    assert reopened.check_due()


@pytest.mark.parametrize(
    "missing",
    [
        "py_modules/decky_mods/service.py",
        "py_modules/decky_mods/re_setup.py",
        "py_modules/libarchive/read.py",
        "data/games.json",
    ],
)
@pytest.mark.parametrize("empty", [False, True])
def test_signed_package_missing_runtime_is_rejected(tmp_path, signing, monkeypatch, missing, empty):
    original = io.BytesIO(package())
    output = io.BytesIO()
    target = "DeckyMods/" + missing
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(output, "w") as archive:
        for entry in source.infolist():
            if entry.filename != target:
                archive.writestr(entry, source.read(entry))
        if empty:
            archive.writestr(target, b"")
    update, _ = manager(tmp_path, signing, monkeypatch, content=output.getvalue())
    with pytest.raises(ModsError, match="结构"):
        update.prepare()


def test_failed_settings_save_preserves_live_and_persisted_preferences(
    tmp_path, signing, monkeypatch
):
    update, _ = manager(tmp_path, signing, monkeypatch)
    previous = update.check()

    def fail(*args):
        raise OSError("disk full")

    monkeypatch.setattr(update, "_save", fail)
    with pytest.raises(ModsError, match="保存"):
        update.configure("http://192.168.50.99:8767", False)
    assert update.status() == previous
    reopened = UpdateManager(signing[0], update.directory, "0.1.2")
    assert reopened.status()["source"] == previous["source"]
    assert reopened.status()["auto_check"] == previous["auto_check"]


def test_no_source_reports_honest_disabled_download(tmp_path, signing):
    update = UpdateManager(signing[0], tmp_path / "updates", "0.1.2")
    status = update.status()
    assert status["source"] is None
    assert status["auto_check"] is True
    assert status["available"] is False
    assert not update.check_due()
    with pytest.raises(ModsError, match="更新来源"):
        update.prepare()


def test_signed_update_check_prepare_and_persistent_preferences(tmp_path, signing, monkeypatch):
    update, payloads = manager(tmp_path, signing, monkeypatch)
    assert update.check_due()
    checked = update.check()
    assert checked["available"] and checked["latest_version"] == "0.1.3"
    assert checked["checked_at"]
    assert not update.check_due()
    artifact = update.prepare()
    path = Path(artifact["artifact"].removeprefix("file://"))
    assert path.read_bytes() == payloads["mods.zip"]
    assert artifact["sha256"] == hashlib.sha256(payloads["mods.zip"]).hexdigest()
    assert os.stat(path).st_mode & 0o777 == 0o600
    assert os.stat(path.parent).st_mode & 0o777 == 0o700
    update.configure("http://192.168.50.10:8767", False)
    reopened = UpdateManager(signing[0], path.parent, "0.1.2")
    assert not reopened.status()["auto_check"]
    assert not reopened.check_due()


@pytest.mark.parametrize(
    "source",
    [
        "http://127.0.0.1:8767",
        "http://169.254.1.1:8767",
        "http://example.com",
        "http://192.168.50.10:8767/path",
        "http://u:p@192.168.50.10",
        "http://192.168.50.10?token=private",
        "https://example.com",
        "https://github.com/evil/DeckyMods/releases/latest/download",
        "https://github.com/18798aa12/DeckyMods/releases/latest/download?token=private",
        "http://192.168.50.10\n",
        "file:///tmp/package",
        "http://[::1]",
    ],
)
def test_reject_untrusted_sources_without_overwriting_preference(tmp_path, signing, source):
    update = UpdateManager(signing[0], tmp_path / "updates", "0.1.2")
    with pytest.raises(ModsError):
        update.configure(source, True)
    assert update.status()["source"] is None


def test_accept_exact_official_github_source(tmp_path, signing):
    update = UpdateManager(signing[0], tmp_path / "updates", "0.1.2")
    checked = update.configure(
        "https://github.com/18798aa12/DeckyMods/releases/latest/download/", True
    )
    assert checked["source"].endswith("/download")


def test_reject_tampered_signature_and_do_not_cache_available(tmp_path, signing, monkeypatch):
    update, payloads = manager(tmp_path, signing, monkeypatch)
    assert update.check()["available"]
    payloads["update.json"] = payloads["update.json"].replace(b"0.1.3", b"9.9.9")
    checked = update.check()
    assert not checked["available"]
    assert checked["error"] and "签名" in checked["error"]
    assert "192.168" not in checked["error"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"schema": 2},
        {"version": "bad"},
        {"size": -1},
        {"size": 33 * 1024 * 1024},
        {"sha256": "bad"},
        {"filename": "../DeckyMods-v0.1.3.zip"},
        {"url": "http://evil.example/payload"},
        {"size": True},
    ],
)
def test_reject_invalid_signed_manifest(tmp_path, signing, monkeypatch, overrides):
    update, _ = manager(tmp_path, signing, monkeypatch, **overrides)
    assert update.check()["error"]
    with pytest.raises(ModsError):
        update.prepare()


def test_downgrade_is_not_installable(tmp_path, signing, monkeypatch):
    update, _ = manager(tmp_path, signing, monkeypatch, content=package("0.1.1"), version="0.1.1")
    assert not update.check()["available"]
    with pytest.raises(ModsError, match="更新"):
        update.prepare()


def test_corrupt_artifact_rejected_even_after_good_check(tmp_path, signing, monkeypatch):
    update, payloads = manager(tmp_path, signing, monkeypatch)
    update.check()
    payloads["mods.zip"] += b"tamper"
    with pytest.raises(ModsError, match="校验"):
        update.prepare()
    assert not list((tmp_path / "private-updates").glob("*.zip"))


@pytest.mark.parametrize(
    "content",
    [
        package(flags=["root"]),
        package(version="0.1.4"),
        package(extra="../outside"),
        package(extra="DeckyMods/../../outside"),
        package(extra="Other/evil"),
        b"not a zip",
    ],
)
def test_valid_signature_cannot_authorize_wrong_package(tmp_path, signing, monkeypatch, content):
    update, _ = manager(tmp_path, signing, monkeypatch, content=content)
    with pytest.raises(ModsError):
        update.prepare()


def test_symlink_member_rejected(tmp_path, signing, monkeypatch):
    output = io.BytesIO(package())
    with zipfile.ZipFile(output, "a") as archive:
        entry = zipfile.ZipInfo("DeckyMods/linked")
        entry.create_system = 3
        entry.external_attr = 0o120777 << 16
        archive.writestr(entry, "/etc/passwd")
    update, _ = manager(tmp_path, signing, monkeypatch, content=output.getvalue())
    with pytest.raises(ModsError):
        update.prepare()


def test_duplicate_case_collisions_rejected(tmp_path, signing, monkeypatch):
    output = io.BytesIO(package())
    with zipfile.ZipFile(output, "a") as archive:
        archive.writestr("DeckyMods/MAIN.py", "collision")
    update, _ = manager(tmp_path, signing, monkeypatch, content=output.getvalue())
    with pytest.raises(ModsError):
        update.prepare()


def test_private_failure_does_not_leak_details(tmp_path, signing, monkeypatch):
    update, _ = manager(tmp_path, signing, monkeypatch)

    def fail(_url, _limit):
        raise OSError("PRIVATE host and password")

    monkeypatch.setattr(update, "_fetch", fail)
    status = update.check()
    assert status["error"]
    assert "PRIVATE" not in status["error"]
    assert not update.check_due()


def test_prepared_handoff_preserves_preferences_only_briefly(tmp_path, signing, monkeypatch):
    from datetime import UTC, datetime, timedelta

    update, _ = manager(tmp_path, signing, monkeypatch)
    assert not update.installation_pending()
    prepared = update.prepare()
    assert update.installation_pending()
    reopened = UpdateManager(signing[0], update.directory, "0.1.3")
    assert reopened.installation_pending()
    reopened._state["prepared"]["created_at"] = (
        datetime.now(UTC) - timedelta(minutes=6)
    ).isoformat()
    assert not reopened.installation_pending()
    Path(prepared["artifact"].removeprefix("file://")).write_bytes(b"external edit")
    assert not update.installation_pending()


def test_signer_cannot_be_replaced_by_update(tmp_path, signing, monkeypatch):
    update, payloads = manager(tmp_path, signing, monkeypatch)
    output = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(payloads["mods.zip"])) as original,
        zipfile.ZipFile(output, "w") as archive,
    ):
        for entry in original.infolist():
            value = (
                b"other-key"
                if entry.filename.endswith("update-allowed-signers")
                else original.read(entry)
            )
            archive.writestr(entry, value)
    data = output.getvalue()
    raw, signature = feed(tmp_path, signing[1], data)
    payloads.update({"update.json": raw, "update.json.sig": signature, "mods.zip": data})
    with pytest.raises(ModsError):
        update.prepare()


@pytest.mark.parametrize("kind", ["fifo", "rootfile", "fileparent", "unsupported-compression"])
def test_special_or_conflicting_members_are_blocked(tmp_path, signing, monkeypatch, kind):
    output = io.BytesIO(package())
    with zipfile.ZipFile(output, "a") as archive:
        if kind == "fifo":
            entry = zipfile.ZipInfo("DeckyMods/pipe")
            entry.create_system = 3
            entry.external_attr = 0o010644 << 16
            archive.writestr(entry, "fifo")
        elif kind == "rootfile":
            archive.writestr("DeckyMods", "root-file")
        elif kind == "fileparent":
            archive.writestr("DeckyMods/file-parent", "parent")
            archive.writestr("DeckyMods/file-parent/child", "child")
        else:
            archive.writestr("DeckyMods/bzip", b"compressed", compress_type=zipfile.ZIP_BZIP2)
    update, _ = manager(tmp_path, signing, monkeypatch, content=output.getvalue())
    with pytest.raises(ModsError):
        update.prepare()


def test_corrupt_preferences_are_visible_without_leaking_content(tmp_path, signing):
    directory = tmp_path / "updates"
    directory.mkdir()
    (directory / "preferences.json").write_text("PRIVATE garbage")
    update = UpdateManager(signing[0], directory, "0.1.2")
    assert "无法读取" in update.status()["error"]
    assert "PRIVATE" not in update.status()["error"]
    assert update.configure("", True)["error"] is None


def test_transport_rejects_lan_redirect_and_bounds_content(monkeypatch):
    from decky_mods.update_feed import fetch

    class Response:
        status = 302
        headers = {"Location": "https://attacker.example/payload"}
        content = b"too large"

        def getheader(self, name, default=None):
            return self.headers.get(name, default)

        def close(self):
            return None

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, amount):
            return self.content[:amount]

    response = Response()

    class Connection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            assert "Authorization" not in kwargs.get("headers", {})

        def getresponse(self):
            return response

        def close(self):
            return None

    monkeypatch.setattr("decky_mods.update_feed.http.client.HTTPConnection", Connection)
    source = "http://192.168.50.10:8767"
    with pytest.raises(ModsError, match="跳转"):
        fetch(source + "/update.json", 4, source=source)
    response.status = 200
    response.headers = {}
    with pytest.raises(ModsError, match="大小限制"):
        fetch(source + "/update.json", 4, source=source)
    response.content = b"data"
    assert fetch(source + "/update.json", 4, source=source) == b"data"
    response.headers = {"Content-Length": "9"}
    with pytest.raises(ModsError, match="大小限制"):
        fetch(source + "/update.json", 4, source=source)


@pytest.mark.parametrize(
    "metadata",
    [
        {
            "remote_binary": [
                {
                    "name": "../../root-payload",
                    "url": "https://attacker.example",
                    "sha256hash": "a" * 64,
                }
            ]
        },
        {
            "remote_binary": [
                {
                    "name": "payload",
                    "url": "https://github.com/trusted/tool",
                    "sha256hash": "a" * 64,
                }
            ]
        },
        {"remote_binary": {"external": "https://attacker.example"}},
    ],
)
def test_native_installer_must_not_fetch_extra_executable_payloads(
    tmp_path, signing, monkeypatch, metadata
):
    update, _ = manager(tmp_path, signing, monkeypatch, content=package(metadata=metadata))
    with pytest.raises(ModsError, match="校验"):
        update.prepare()


@pytest.mark.parametrize("api_version", [None, 0, 2, True, "1"])
def test_only_supported_decky_api_version_can_be_updated(
    tmp_path, signing, monkeypatch, api_version
):
    update, _ = manager(tmp_path, signing, monkeypatch, content=package(api_version=api_version))
    with pytest.raises(ModsError, match="校验"):
        update.prepare()
