"""File picker starts in the actual user's configured download directory."""

import pytest
from decky_mods.imports import LocalArchives


def test_import_picker_prefers_xdg_download_directory(tmp_path):
    home = tmp_path / "custom-user"
    (home / "Downloads").mkdir(parents=True)
    (home / "下载位置").mkdir()
    (home / ".config").mkdir()
    (home / ".config/user-dirs.dirs").write_text('XDG_DOWNLOAD_DIR="$HOME/下载位置"\n')
    assert LocalArchives(home).start_directory() == str(home / "下载位置")


def test_import_picker_uses_home_when_no_download_directory_exists(tmp_path):
    assert LocalArchives(tmp_path).start_directory() == str(tmp_path)


def test_import_picker_ignores_outside_xdg_directory(tmp_path):
    (tmp_path / ".config").mkdir()
    (tmp_path / ".config/user-dirs.dirs").write_text('XDG_DOWNLOAD_DIR="/tmp"\n')
    assert LocalArchives(tmp_path).start_directory() == str(tmp_path)


def test_import_picker_prefers_download_when_xdg_settings_are_out_of_order(tmp_path):
    for directory in ("Downloads", "自定义桌面", "自定义文档", "自定义下载", ".config"):
        (tmp_path / directory).mkdir()
    (tmp_path / ".config/user-dirs.dirs").write_text(
        'XDG_DESKTOP_DIR="$HOME/自定义桌面"\n'
        'XDG_DOCUMENTS_DIR="$HOME/自定义文档"\n'
        'XDG_DOWNLOAD_DIR="$HOME/自定义下载"\n'
    )

    assert LocalArchives(tmp_path).start_directory() == str(tmp_path / "自定义下载")


@pytest.mark.parametrize("download", ["missing", "outside", "symlink", "ancestor_symlink"])
def test_import_picker_uses_standard_downloads_before_other_xdg_directories(tmp_path, download):
    home = tmp_path / "home"
    for directory in ("Downloads", "自定义桌面", "自定义文档", ".config"):
        (home / directory).mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "nested").mkdir()
    configured = home / "不存在的下载"
    if download == "outside":
        configured = outside
    elif download in {"symlink", "ancestor_symlink"}:
        (home / "链接").symlink_to(outside, target_is_directory=True)
        configured = home / "链接"
        if download == "ancestor_symlink":
            configured /= "nested"
    (home / ".config/user-dirs.dirs").write_text(
        'XDG_DESKTOP_DIR="$HOME/自定义桌面"\n'
        'XDG_DOCUMENTS_DIR="$HOME/自定义文档"\n'
        f'XDG_DOWNLOAD_DIR="{configured}"\n'
    )

    assert LocalArchives(home).start_directory() == str(home / "Downloads")


def test_import_picker_falls_back_to_other_allowed_directory_before_home(tmp_path):
    (tmp_path / ".config").mkdir()
    (tmp_path / "自定义文档").mkdir()
    (tmp_path / ".config/user-dirs.dirs").write_text(
        'XDG_DOWNLOAD_DIR="$HOME/不存在的下载"\nXDG_DOCUMENTS_DIR="$HOME/自定义文档"\n'
    )

    assert LocalArchives(tmp_path).start_directory() == str(tmp_path / "自定义文档")


def test_import_directory_allowlist_keeps_all_configured_and_standard_paths(tmp_path):
    (tmp_path / ".config").mkdir()
    (tmp_path / ".config/user-dirs.dirs").write_text(
        'XDG_DESKTOP_DIR="$HOME/自定义桌面"\n'
        'XDG_DOCUMENTS_DIR="$HOME/自定义文档"\n'
        'XDG_DOWNLOAD_DIR="$HOME/自定义下载"\n'
    )

    assert set(LocalArchives(tmp_path).directories()) == {
        tmp_path / directory
        for directory in (
            "自定义桌面",
            "自定义文档",
            "自定义下载",
            "Downloads",
            "Documents",
            "Desktop",
            "下载",
            "文档",
            "桌面",
        )
    }
