"""Modern Resident Evil layouts use reviewed REFramework loader paths."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

import pytest
from decky_mods.deployment import Deployment
from decky_mods.re_engine import (
    CONFIG_NAME,
    LOOSE_KEY,
    PAK_DIRECTORY_KEY,
    config_status,
    plan_re_engine,
    read_reframework_flags,
)

MODERN_RE = (
    "residentevil22019",
    "residentevil32020",
    "residentevil42023",
    "residentevil7",
    "residentevilvillage",
    "residentevilrequiem",
)


def put(root: Path, relative: str, data: bytes = b"fixture") -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def game(root: Path, ident: str = "residentevil7") -> dict:
    return {
        "id": ident,
        "path": str(root),
        "requirements": ["使用匹配游戏版本的 MOD。"],
        "build_id": "1",
        "running": False,
        "adapter_config": {
            "native_config": CONFIG_NAME,
            **(
                {
                    "re_pak_prefix": "re_chunk_000.pak.patch_",
                    "re_base_pak": "re_chunk_000.pak",
                }
                if ident == "residentevil42023"
                else {}
            ),
        },
    }


def configured(root: Path, loose: bool = True, pak: bool = True) -> None:
    put(root, "dinput8.dll")
    put(
        root,
        CONFIG_NAME,
        f"{LOOSE_KEY}={str(loose).lower()}\n{PAK_DIRECTORY_KEY}={str(pak).lower()}\n".encode(),
    )


def plan(root: Path, paths: list[str], ident: str = "residentevil7") -> dict:
    return plan_re_engine(game(root, ident), [PurePosixPath(name) for name in paths], root)


@pytest.mark.parametrize("ident", MODERN_RE)
def test_each_modern_title_maps_loose_resources_with_shared_config(
    tmp_path: Path, ident: str
) -> None:
    configured(tmp_path)
    result = plan(tmp_path, ["CoolMod/natives/STM/character/outfit.mesh.123"], ident)
    assert result["blocked_reason"] is None
    assert result["files"] == [
        {
            "source": "CoolMod/natives/STM/character/outfit.mesh.123",
            "target": "natives/STM/character/outfit.mesh.123",
        }
    ]
    assert result.get("config_requirements", []) == []
    assert any("游戏内" in warning for warning in result["warnings"])


@pytest.mark.parametrize("ident", MODERN_RE)
def test_each_modern_title_roundtrip_resource_disable_enable_uninstall(
    tmp_path: Path, ident: str
) -> None:
    root, archive = tmp_path / "game", tmp_path / "archive"
    configured(root)
    filename = "natives/STM/character/outfit.mesh.123"
    put(archive, filename, b"modded costume")
    selected = game(root, ident)
    result = plan(root, [filename], ident)
    engine = Deployment(tmp_path / "state")
    prepared = engine.prepare(selected, "Costume", archive, result)
    assert prepared["can_install"]
    installed = engine.install(selected, prepared["id"])
    assert (root / filename).read_bytes() == b"modded costume"
    engine.set_enabled(selected, installed["id"], False)
    assert not (root / filename).exists()
    engine.set_enabled(selected, installed["id"], True)
    assert (root / filename).read_bytes() == b"modded costume"
    engine.uninstall(selected, installed["id"])
    assert not (root / filename).exists()
    assert read_reframework_flags(root)[LOOSE_KEY]


def test_script_data_preserved_and_only_outer_metadata_ignored(tmp_path: Path) -> None:
    put(tmp_path, "dinput8.dll")
    paths = [
        "Wrapper/reframework/autorun/Mod/main.lua",
        "Wrapper/reframework/autorun/Mod/config.json",
        "Wrapper/reframework/autorun/Mod/images/showcase.png",
        "Wrapper/reframework/autorun/Mod/readme.txt",
        "Wrapper/reframework/plugins/Companion.dll",
        "Wrapper/modinfo.ini",
        "Wrapper/showcase.png",
        "README.md",
    ]
    result = plan(tmp_path, paths)
    assert result["blocked_reason"] is None
    assert len(result["files"]) == 5
    assert any(item["target"].endswith("config.json") for item in result["files"])
    assert any(item["target"].endswith("images/showcase.png") for item in result["files"])
    assert any("WINEDLLOVERRIDES" in item for item in result["requirements"])


@pytest.mark.parametrize("ident", MODERN_RE)
def test_loader_missing_and_symlinked_is_blocked(tmp_path: Path, ident: str) -> None:
    paths = ["reframework/autorun/mod.lua"]
    assert plan(tmp_path, paths, ident)["blocked_reason"]
    outside = tmp_path / "outside.dll"
    outside.write_bytes(b"loader")
    (tmp_path / "dinput8.dll").symlink_to(outside)
    assert plan(tmp_path, paths, ident)["blocked_reason"]


def test_false_flags_produce_safe_mapping_and_explicit_preparation_requirement(
    tmp_path: Path,
) -> None:
    configured(tmp_path, loose=False)
    result = plan(tmp_path, ["natives/STM/object.mesh.123"])
    assert result["blocked_reason"] is None
    assert result["config_requirements"] == [LOOSE_KEY]
    assert any("确认安装" in item for item in result["warnings"])
    assert read_reframework_flags(tmp_path)[LOOSE_KEY] is False


def test_missing_or_wrong_name_config_does_not_satisfy_loose_loader(tmp_path: Path) -> None:
    put(tmp_path, "dinput8.dll")
    put(tmp_path, "re7_fw_config.txt", f"{LOOSE_KEY}=true\n".encode())
    result = plan(tmp_path, ["natives/STM/object.mesh.123"])
    assert result["blocked_reason"] and not result["files"]
    assert CONFIG_NAME in result["blocked_reason"]


@pytest.mark.parametrize(
    "content",
    [
        f"{LOOSE_KEY}=false\n{LOOSE_KEY}=true\n".encode(),
        f"{LOOSE_KEY}=definitely\n".encode(),
        f"{LOOSE_KEY}=true\x00\n".encode(),
        b"\xff\xfe",
        b"x" * (512 * 1024 + 1),
    ],
)
def test_malformed_config_blocks_resources(tmp_path: Path, content: bytes) -> None:
    put(tmp_path, "dinput8.dll")
    put(tmp_path, CONFIG_NAME, content)
    assert not config_status(tmp_path)["valid"]
    result = plan(tmp_path, ["natives/STM/object.mesh.123"])
    assert result["blocked_reason"] and not result["files"]


def test_config_status_missing_symlink_and_false_keys(tmp_path: Path) -> None:
    assert config_status(tmp_path) == {"exists": False, "valid": False, "flags": {}}
    outside = tmp_path / "outside"
    outside.write_text(f"{LOOSE_KEY}=true\n")
    (tmp_path / CONFIG_NAME).symlink_to(outside)
    assert config_status(tmp_path) == {"exists": True, "valid": False, "flags": {}}
    (tmp_path / CONFIG_NAME).unlink()
    put(tmp_path, CONFIG_NAME, b"# defaults\nOther_Value=12\n")
    assert config_status(tmp_path) == {
        "exists": True,
        "valid": True,
        "flags": {LOOSE_KEY: False, PAK_DIRECTORY_KEY: False},
    }


def test_re9_pak_directory_requires_both_flags_and_preserves_subpaths(tmp_path: Path) -> None:
    configured(tmp_path, loose=False, pak=False)
    result = plan(tmp_path, ["Cool/pak_mods/mod/Costume.pak"], "residentevilrequiem")
    assert result["blocked_reason"] is None
    assert result["files"] == [
        {"source": "Cool/pak_mods/mod/Costume.pak", "target": "pak_mods/mod/Costume.pak"}
    ]
    assert result["config_requirements"] == [LOOSE_KEY, PAK_DIRECTORY_KEY]
    configured(tmp_path)
    assert not plan(tmp_path, ["Costume.pak"], "residentevilrequiem")["blocked_reason"]
    assert plan(tmp_path, ["Costume.PAK"], "residentevilrequiem")["blocked_reason"]


def test_re9_pak_directory_roundtrip_preserves_other_mods_and_loader_settings(
    tmp_path: Path,
) -> None:
    root, archive = tmp_path / "game", tmp_path / "archive"
    configured(root)
    put(root, "pak_mods/existing.pak", b"preexisting mod")
    put(archive, "Cool/pak_mods/costume.pak", b"new costume")
    selected = game(root, "residentevilrequiem")
    result = plan(root, ["Cool/pak_mods/costume.pak"], selected["id"])
    engine = Deployment(tmp_path / "state")
    prepared = engine.prepare(selected, "Costume", archive, result)
    installed = engine.install(selected, prepared["id"])
    deployed = root / "pak_mods/costume.pak"
    assert deployed.read_bytes() == b"new costume"
    engine.set_enabled(selected, installed["id"], False)
    assert not deployed.exists()
    engine.set_enabled(selected, installed["id"], True)
    assert deployed.read_bytes() == b"new costume"
    engine.uninstall(selected, installed["id"])
    assert not deployed.exists()
    assert (root / "pak_mods/existing.pak").read_bytes() == b"preexisting mod"
    assert read_reframework_flags(root) == {LOOSE_KEY: True, PAK_DIRECTORY_KEY: True}


@pytest.mark.parametrize("ident", MODERN_RE[:-1])
def test_pak_directory_not_assumed_available_for_older_games(tmp_path: Path, ident: str) -> None:
    configured(tmp_path)
    assert plan(tmp_path, ["pak_mods/Costume.pak"], ident)["blocked_reason"]


def test_re4_patchpak_keeps_base_archive_guard_and_numbering_kind(tmp_path: Path) -> None:
    put(tmp_path, "dinput8.dll")
    paths = ["Cool/re_chunk_000.pak.patch_007.pak"]
    assert plan(tmp_path, paths, "residentevil42023")["blocked_reason"]
    put(tmp_path, "re_chunk_000.pak")
    result = plan(tmp_path, paths, "residentevil42023")
    assert result["blocked_reason"] is None
    assert result["files"][0]["kind"] == "re_pak"
    assert result["files"][0]["target"] == "re_chunk_000.pak.patch_007.pak"
    assert plan(tmp_path, paths * 2, "residentevil42023")["blocked_reason"]


@pytest.mark.parametrize("ident", ["residentevil22019", "residentevil32020", "residentevil7"])
@pytest.mark.parametrize("variant", ["x64", "STM"])
def test_rt_nonrt_warning_never_claims_directory_proves_compatibility(
    tmp_path: Path, ident: str, variant: str
) -> None:
    configured(tmp_path)
    result = plan(tmp_path, [f"natives/{variant}/object.mesh.123"], ident)
    assert result["blocked_reason"] is None
    assert any("RT" in warning and "非 RT" in warning for warning in result["warnings"])


@pytest.mark.parametrize(
    "paths",
    [
        ["OptionA/natives/STM/a.mesh.123", "OptionB/natives/STM/b.mesh.123"],
        ["natives/STM/a.mesh.123", "natives/x64/b.mesh.123"],
        ["reframework/autorun/mod.lua", "setup.exe"],
        ["natives/STM/mod.mesh.123", "dxgi.dll"],
        ["fomod/moduleconfig.xml", "natives/STM/a.mesh.123"],
        ["reframework/plugins/readme.cfg"],
        ["reframework/config.ini"],
        ["natives/a"],
        ["natives/STM/run.exe"],
        ["reframework/autorun/run.bat"],
        ["pak_mods/mod.pak", "pak_mods/setup.json"],
        ["reframework/autorun/one.lua", "different/readme.txt"],
    ],
)
def test_ambiguous_and_unreviewed_packages_fail_closed(tmp_path: Path, paths: list[str]) -> None:
    configured(tmp_path)
    assert plan(tmp_path, paths, "residentevilrequiem")["blocked_reason"]


def test_planning_does_not_mutate_registry_or_config(tmp_path: Path) -> None:
    configured(tmp_path, loose=False)
    selected = game(tmp_path)
    original = json.dumps(selected, sort_keys=True)
    config_bytes = (tmp_path / CONFIG_NAME).read_bytes()
    result = plan_re_engine(selected, [PurePosixPath("natives/STM/file.mesh.123")], tmp_path)
    assert result["blocked_reason"] is None
    assert json.dumps(selected, sort_keys=True) == original
    assert (tmp_path / CONFIG_NAME).read_bytes() == config_bytes
