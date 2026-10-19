"""Distribution boundaries are allowlisted, reproducible, and credential-free."""

import zipfile
from pathlib import Path

import pytest

from scripts.package import build_zip, vendor_archive
from scripts.sanitize import inspect_bytes


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
