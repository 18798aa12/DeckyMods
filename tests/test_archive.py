import stat
import threading
import zipfile

import pytest
from decky_mods.archive import extract_archive
from decky_mods.errors import ModsError


def make_zip(path, entries):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            archive.writestr(name, data)


def test_archive_reads_regular_files_without_extractall(tmp_path):
    source = tmp_path / "mod.zip"
    make_zip(source, [("Wrapper/mod.pak", b"pak-data"), ("Wrapper/readme.txt", b"read me")])
    result = extract_archive(source, tmp_path / "out")
    assert sorted(result) == ["Wrapper/mod.pak", "Wrapper/readme.txt"]
    assert (tmp_path / "out/Wrapper/mod.pak").read_bytes() == b"pak-data"


@pytest.mark.parametrize(
    "name",
    [
        "../escape",
        "/escape",
        "C:\\escape",
        "a/../../b",
        "a\\..\\b",
        "a:stream",
        ".config/key",
        "a//b",
        "a/./b",
    ],
)
def test_rejects_unsafe_archive_paths(tmp_path, name):
    source = tmp_path / "bad.zip"
    make_zip(source, [(name, b"no")])
    with pytest.raises(ModsError):
        extract_archive(source, tmp_path / "out")
    assert not (tmp_path / "escape").exists()


def test_rejects_archive_symlink(tmp_path):
    source = tmp_path / "bad.zip"
    with zipfile.ZipFile(source, "w") as archive:
        entry = zipfile.ZipInfo("linked")
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(entry, "../escape")
        archive.writestr("linked/file", "no")
    with pytest.raises(ModsError):
        extract_archive(source, tmp_path / "out")


@pytest.mark.parametrize(
    "entries",
    [
        [("a.pak", b"1"), ("A.pak", b"2")],
        [("a.pak", b"1"), ("a.pak", b"2")],
        [("a", b"1"), ("a/b", b"2")],
    ],
)
def test_rejects_colliding_archive_names(tmp_path, entries):
    source = tmp_path / "bad.zip"
    make_zip(source, entries)
    with pytest.raises(ModsError):
        extract_archive(source, tmp_path / "out")


def test_archive_expansion_and_count_limits(tmp_path):
    source = tmp_path / "large.zip"
    make_zip(source, [("big.pak", b"a" * 4096)])
    with pytest.raises(ModsError, match="大小|限制"):
        extract_archive(source, tmp_path / "out", max_bytes=100)
    source = tmp_path / "many.zip"
    make_zip(source, [(f"{index}.txt", b"a") for index in range(4)])
    with pytest.raises(ModsError, match="数量|限制"):
        extract_archive(source, tmp_path / "many", max_files=2)


def test_corrupt_empty_cancelled_and_linked_input(tmp_path):
    source = tmp_path / "bad.zip"
    source.write_bytes(b"not an archive")
    with pytest.raises(ModsError):
        extract_archive(source, tmp_path / "out")
    make_zip(source, [])
    with pytest.raises(ModsError):
        extract_archive(source, tmp_path / "empty")
    make_zip(source, [("mod.pak", b"payload")])
    cancel = threading.Event()
    cancel.set()
    with pytest.raises(ModsError, match="取消"):
        extract_archive(source, tmp_path / "cancel", cancel=cancel)
    link = tmp_path / "link.zip"
    link.symlink_to(source)
    with pytest.raises(ModsError):
        extract_archive(link, tmp_path / "linked")


def test_real_7z_reader_uses_same_safety_boundary(tmp_path):
    import libarchive

    source = tmp_path / "mod.7z"
    with libarchive.file_writer(str(source), "7zip") as archive:
        archive.add_file_from_memory("mod.pak", 7, b"payload")
    assert extract_archive(source, tmp_path / "out") == ["mod.pak"]
    assert (tmp_path / "out/mod.pak").read_bytes() == b"payload"
