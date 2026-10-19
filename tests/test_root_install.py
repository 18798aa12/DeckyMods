"""Explicit root layouts retain the reversible deployment boundary."""

from pathlib import Path, PurePosixPath

import pytest
from decky_mods.deployment import Deployment
from decky_mods.errors import ModsError
from decky_mods.root_install import plan_root_files


@pytest.fixture
def game(tmp_path):
    root = tmp_path / "Game"
    root.mkdir()
    return {
        "id": "unadapted",
        "installed": True,
        "adapter": "catalog",
        "path": str(root),
        "build_id": "one",
        "running": False,
        "requirements": ["作者要求的依赖必须先安装"],
    }


def stage(tmp_path, files):
    directory = tmp_path / "staging"
    directory.mkdir(exist_ok=True)
    for relative, contents in files.items():
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents)
    return directory


def test_preserves_wrapper_and_all_resource_extensions_without_writing(game, tmp_path):
    payload = {
        "My MOD/Data/image.png": b"texture",
        "My MOD/Data/language.txt": b"translation",
        "My MOD/settings.ini": b"[configuration]",
        "My MOD/Data/object.bin": b"resource",
        "README.txt": b"Read author instructions",
    }
    staging = stage(tmp_path, payload)
    mapping = plan_root_files(game, staging)
    assert mapping["blocked_reason"] is None
    assert mapping["files"] == [
        {"source": relative, "target": relative} for relative in sorted(payload)
    ]
    assert list(Path(game["path"]).iterdir()) == []
    assert "作者要求的依赖必须先安装" in mapping["requirements"]
    warnings = " ".join(mapping["warnings"])
    assert "根目录" in warnings and "外层目录" in warnings
    assert "前置" in warnings and "合并配置" in warnings and "启动项" in warnings


def test_root_install_roundtrip_restores_original_and_removes_added_assets(game, tmp_path):
    root = Path(game["path"])
    (root / "settings.ini").write_bytes(b"original user settings")
    staging = stage(
        tmp_path,
        {"settings.ini": b"mod settings", "Data/new.png": b"texture", "dinput8.dll": b"dll"},
    )
    mapping = plan_root_files(game, staging)
    engine = Deployment(tmp_path / "state")
    prepared = engine.prepare(game, "Explicit root MOD", staging, mapping)
    assert prepared["conflicts"] == ["settings.ini"]
    with pytest.raises(ModsError, match="覆盖|冲突"):
        engine.install(game, prepared["id"])
    mod = engine.install(game, prepared["id"], True)
    assert (root / "settings.ini").read_bytes() == b"mod settings"
    assert (root / "Data/new.png").read_bytes() == b"texture"
    engine.set_enabled(game, mod["id"], False)
    assert (root / "settings.ini").read_bytes() == b"original user settings"
    assert not (root / "Data/new.png").exists()
    assert not (root / "dinput8.dll").exists()
    engine.set_enabled(game, mod["id"], True)
    assert (root / "Data/new.png").read_bytes() == b"texture"
    engine.uninstall(game, mod["id"])
    assert (root / "settings.ini").read_bytes() == b"original user settings"
    assert not (root / "Data/new.png").exists()
    assert engine.list_mods(game["id"]) == []


@pytest.mark.parametrize("extension", ["dll", "asi", "so"])
def test_loaders_are_preserved_with_execution_warning(game, tmp_path, extension):
    staging = stage(tmp_path, {f"loader.{extension}": b"loader"})
    mapping = plan_root_files(game, staging)
    assert mapping["blocked_reason"] is None
    assert mapping["files"] == [{"source": f"loader.{extension}", "target": f"loader.{extension}"}]
    assert "加载器" in " ".join(mapping["warnings"])


@pytest.mark.parametrize(
    "relative",
    [
        "fomod/ModuleConfig.xml",
        "FOMOD/info.xml",
        "Options/A/Data.bin",
        "Optional Files/Data.bin",
        "Variants/Red/model.bin",
        "Alternative/Blue/model.bin",
        "installer/setup.exe",
        "setup.exe",
        "install.msi",
        "Install.bat",
        "install.cmd",
        "install.ps1",
        "install.sh",
        "install.command",
        "install.vbs",
        "install.desktop",
        "install.app/Contents/MacOS/setup",
        "steamapps/appmanifest_1.acf",
        "compatdata/pfx/user.reg",
    ],
)
def test_installers_options_and_other_library_roots_are_blocked(game, tmp_path, relative):
    staging = stage(tmp_path, {"Data/resource.bin": b"asset", relative: b"installer"})
    mapping = plan_root_files(game, staging)
    assert mapping["blocked_reason"]
    assert mapping["files"] == []


@pytest.mark.parametrize("names", [("DX11", "DX12"), ("x86", "x64"), ("RT", "Non-RT")])
def test_parallel_runtime_versions_require_single_choice(game, tmp_path, names):
    staging = stage(tmp_path, {f"{name}/data.bin": b"asset" for name in names})
    mapping = plan_root_files(game, staging)
    assert mapping["blocked_reason"]
    assert mapping["files"] == []


def test_a_single_x64_resource_directory_is_valid(game, tmp_path):
    staging = stage(tmp_path, {"natives/x64/data.bin": b"asset"})
    assert plan_root_files(game, staging)["blocked_reason"] is None


@pytest.mark.parametrize("contents", [b"#!/bin/sh\nrm -rf ignored", b"#!/usr/bin/env python\n"])
def test_extensionless_executable_scripts_are_blocked(game, tmp_path, contents):
    staging = stage(tmp_path, {"install": contents})
    assert plan_root_files(game, staging)["blocked_reason"]


@pytest.mark.parametrize(
    "relative", [".hidden/a.bin", "Data/.git/config", "C:/escape", "bad\n.bin"]
)
def test_unsafe_relative_paths_raise(game, tmp_path, relative):
    staging = stage(tmp_path, {relative: b"unsafe"})
    with pytest.raises(ModsError):
        plan_root_files(game, staging)


def test_hidden_empty_directory_is_rejected(game, tmp_path):
    staging = stage(tmp_path, {"Data/a.bin": b"asset"})
    (staging / ".ssh").mkdir()
    with pytest.raises(ModsError, match="路径|隐藏"):
        plan_root_files(game, staging)


def test_empty_option_directory_is_not_silently_ignored(game, tmp_path):
    staging = stage(tmp_path, {"Data/a.bin": b"asset"})
    (staging / "01 Optional").mkdir()
    assert plan_root_files(game, staging)["blocked_reason"]


@pytest.mark.parametrize("unsafe", ["../escape.bin", "/outside.bin", "Data/../escape.bin"])
def test_inventory_paths_cannot_traverse_root(game, tmp_path, monkeypatch, unsafe):
    staging = stage(tmp_path, {"safe.bin": b"asset"})
    monkeypatch.setattr("decky_mods.root_install._inventory", lambda _: [PurePosixPath(unsafe)])
    with pytest.raises(ModsError):
        plan_root_files(game, staging)


@pytest.mark.parametrize("kind", ["file", "directory", "staging"])
def test_staging_links_are_never_followed(game, tmp_path, kind):
    staging = stage(tmp_path, {"Data/a.bin": b"asset"})
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private.bin").write_bytes(b"private")
    if kind == "file":
        (staging / "link").symlink_to(outside / "private.bin")
    elif kind == "directory":
        (staging / "link").symlink_to(outside, target_is_directory=True)
    else:
        link = tmp_path / "link"
        link.symlink_to(staging, target_is_directory=True)
        staging = link
    with pytest.raises(ModsError):
        plan_root_files(game, staging)
    assert (outside / "private.bin").read_bytes() == b"private"


def test_target_symlink_cannot_escape_deployment(game, tmp_path):
    root = Path(game["path"])
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "data.bin").write_bytes(b"private")
    (root / "Data").symlink_to(outside, target_is_directory=True)
    staging = stage(tmp_path, {"Data/data.bin": b"mod"})
    mapping = plan_root_files(game, staging)
    engine = Deployment(tmp_path / "state")
    prepared = engine.prepare(game, "root MOD", staging, mapping)
    assert not prepared["can_install"] and "链接" in prepared["blocked_reason"]
    assert (outside / "data.bin").read_bytes() == b"private"


@pytest.mark.parametrize("adapter", ["reframework", "re_legacy", "ue_pak", None])
def test_reviewed_adapters_cannot_be_bypassed(game, tmp_path, adapter):
    staging = stage(tmp_path, {"Data/a.bin": b"asset"})
    mapping = plan_root_files({**game, "adapter": adapter}, staging)
    assert mapping["blocked_reason"]
    assert mapping["files"] == []


@pytest.mark.parametrize("changed", [{"running": True}, {"updating": True}, {"installed": False}])
def test_missing_or_busy_game_is_rejected(game, tmp_path, changed):
    staging = stage(tmp_path, {"Data/a.bin": b"asset"})
    with pytest.raises(ModsError):
        plan_root_files({**game, **changed}, staging)


def test_empty_archive_cannot_install(game, tmp_path):
    mapping = plan_root_files(game, stage(tmp_path, {}))
    assert mapping["blocked_reason"]
    assert mapping["files"] == []


@pytest.mark.parametrize("location", ["missing", "relative", "link", "file"])
def test_invalid_game_root_is_rejected(game, tmp_path, location):
    staging = stage(tmp_path, {"a.bin": b"asset"})
    if location == "missing":
        path = str(tmp_path / "missing")
    elif location == "relative":
        path = "relative/path"
    elif location == "link":
        link = tmp_path / "game-link"
        link.symlink_to(Path(game["path"]), target_is_directory=True)
        path = str(link)
    else:
        file = tmp_path / "not-directory"
        file.write_bytes(b"file")
        path = str(file)
    with pytest.raises(ModsError):
        plan_root_files({**game, "path": path}, staging)


def test_case_conflicts_are_rejected(game, tmp_path):
    staging = stage(tmp_path, {"Data/a.bin": b"first", "Data/A.bin": b"second"})
    if len(list((staging / "Data").iterdir())) != 2:
        pytest.skip("requires a case-sensitive filesystem")
    mapping = plan_root_files(game, staging)
    assert mapping["blocked_reason"]
    assert mapping["files"] == []


def test_external_changes_are_preserved_when_uninstalling(game, tmp_path):
    staging = stage(tmp_path, {"Data/a.bin": b"mod"})
    engine = Deployment(tmp_path / "state")
    plan = engine.prepare(game, "root MOD", staging, plan_root_files(game, staging))
    mod = engine.install(game, plan["id"])
    target = Path(game["path"]) / "Data/a.bin"
    target.write_bytes(b"external update")
    with pytest.raises(ModsError, match="修改|冲突"):
        engine.uninstall(game, mod["id"])
    assert target.read_bytes() == b"external update"


def test_unreadable_staged_file_has_actionable_sanitized_error(game, tmp_path, monkeypatch):
    staging = stage(tmp_path, {"a.bin": b"asset"})

    def unreadable(*args, **kwargs):
        raise PermissionError("private filesystem detail")

    monkeypatch.setattr("decky_mods.root_install.os.open", unreadable)
    with pytest.raises(ModsError, match="重新导入") as caught:
        plan_root_files(game, staging)
    assert "private" not in str(caught.value)


def test_unreadable_subdirectory_never_produces_partial_plan(game, tmp_path, monkeypatch):
    staging = stage(tmp_path, {"a.bin": b"asset"})
    monkeypatch.setattr("decky_mods.root_install._inventory", lambda _: [PurePosixPath("a.bin")])

    def unreadable_walk(*args, onerror, **kwargs):
        onerror(PermissionError("private filesystem detail"))
        return iter(())

    monkeypatch.setattr("decky_mods.root_install.os.walk", unreadable_walk)
    with pytest.raises(ModsError, match="完整读取") as caught:
        plan_root_files(game, staging)
    assert "private" not in str(caught.value)


def test_root_install_rejects_case_mismatch_with_existing_game_paths(game, tmp_path):
    root = Path(game["path"])
    (root / "Data").mkdir()
    (root / "Data/config.ini").write_bytes(b"original")
    mapping = plan_root_files(game, stage(tmp_path, {"data/config.ini": b"mod"}))
    assert mapping["blocked_reason"] and "大小写" in mapping["blocked_reason"]
