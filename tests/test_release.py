"""Distribution boundaries are allowlisted, reproducible, and credential-free."""

import json
import zipfile
from pathlib import Path

import pytest

from scripts.package import build_zip, vendor_archive
from scripts.sanitize import inspect_bytes


def test_required_runtime_inventory_covers_every_first_party_module():
    from decky_mods.package_layout import REQUIRED_FILES

    root = Path(__file__).resolve().parents[1]
    modules = {
        path.relative_to(root).as_posix() for path in (root / "py_modules/decky_mods").glob("*.py")
    }
    assert modules <= REQUIRED_FILES


def test_zip_is_reproducible_and_rejects_link_inputs(tmp_path):
    source = tmp_path / "stage"
    source.mkdir()
    (source / "main.py").write_text("pass\n")
    first, second = tmp_path / "a.zip", tmp_path / "b.zip"
    build_zip(source, first)
    build_zip(source, second)
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == ["DeckyMods/main.py"]
    (source / "link").symlink_to(source / "main.py")
    with pytest.raises(ValueError, match="link"):
        build_zip(source, second)


def test_vendor_only_extracts_reviewed_modules_and_license(tmp_path):
    wheel = tmp_path / "archive.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("libarchive/__init__.py", "pass\n")
        archive.writestr("libarchive/ffi.py", "pass\n")
        archive.writestr("libarchive/read.py", "pass\n")
        archive.writestr("libarchive/entry.py", "pass\n")
        archive.writestr("libarchive_c-5.3.dist-info/licenses/LICENSE.md", "CC0\n")
        archive.writestr("ignored.so", "native binary")
        archive.writestr("../../escape.py", "unsafe")
    vendor_archive(wheel, tmp_path / "stage")
    assert (tmp_path / "stage/py_modules/libarchive/ffi.py").exists()
    assert not (tmp_path / "escape.py").exists()
    assert not (tmp_path / "stage/ignored.so").exists()
    assert (tmp_path / "stage/licenses/libarchive-c-LICENSE").read_text() == "CC0\n"


@pytest.mark.parametrize(
    "payload",
    [b"nxm://game/mods/1/files/2?key=private&expires=123", b"/Users/ExampleUser/private"],
)
def test_release_sanitizer_rejects_private_material(payload):
    with pytest.raises(ValueError):
        inspect_bytes("sample.txt", payload)


def test_release_sanitizer_accepts_generic_examples():
    inspect_bytes("README.md", b"API key stays local. https://www.nexusmods.com/game/mods/1")


def test_release_sanitizer_can_scan_its_own_detection_code():
    from scripts import sanitize

    inspect_bytes("scripts/sanitize.py", Path(sanitize.__file__).read_bytes())


@pytest.mark.parametrize("label", ["apikey", "api_key", "apiKey", "NEXUS_API_KEY"])
def test_sanitizer_rejects_labelled_credentials_with_base64_characters(label):
    credential = ("aB/7+z-" * 8) + "=="
    for payload in (json.dumps({label: credential}), f'{label} = "{credential}"'):
        with pytest.raises(ValueError) as caught:
            inspect_bytes("export.txt", payload.encode())
        assert credential not in str(caught.value)


def test_sanitizer_rejects_real_account_shape_outside_account_filename():
    credential = "synthetic/" * 8
    payload = json.dumps({"auth": {"connected": True}, "key": credential}).encode()
    with pytest.raises(ValueError):
        inspect_bytes("copied-settings.txt", payload)


@pytest.mark.parametrize("field", ["token", "key", "md5", "X-Amz-Signature", "signature"])
@pytest.mark.parametrize("host", ["cf-files.nexusmods.com", "files.nexus-cdn.com"])
def test_sanitizer_rejects_signed_https_download_grants(host, field):
    payload = f"https://{host}/download.zip?expires=123&{field}=synthetic".encode()
    with pytest.raises(ValueError):
        inspect_bytes("notes.txt", payload)


def test_sanitizer_accepts_ordinary_nexus_page_and_noncredential_keys():
    inspect_bytes("notes.txt", b"https://www.nexusmods.com/game/mods/1?tab=files&file_id=2")
    inspect_bytes("data.json", json.dumps({"key": "public catalogue id" * 5}).encode())


def test_sanitizer_rejects_unquoted_shell_credentials():
    payload = "export NEXUS_API_KEY=" + ("synthetic/credential+" * 4)
    with pytest.raises(ValueError):
        inspect_bytes("README.md", payload.encode())


def test_sanitizer_rejects_html_escaped_signed_link():
    payload = b"https://cf-files.nexusmods.com/file.zip?expires=123&amp;token=synthetic"
    with pytest.raises(ValueError):
        inspect_bytes("notes.html", payload)
