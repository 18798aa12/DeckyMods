"""Legacy RE adapters map only author-packaged, existing resource replacements."""

from pathlib import Path, PurePosixPath

import pytest
from decky_mods.deployment import Deployment
from decky_mods.re_legacy import plan_legacy

TITLES = [
    ("residentevil0biohazard0hdremaster", "nativePC"),
    ("residentevilbiohazardhdremaster", "nativePC"),
    ("residentevil4", "BIO4"),
    ("residentevil5", "nativePC_MT"),
    ("residentevil6", "nativePC"),
    ("residentevilrevelations", "nativePC"),
    ("residentevilrevelations2", "nativePC"),
]


def make_game(tmp_path, game_id="residentevil6", anchor="nativePC"):
    root = tmp_path / "game"
    root.mkdir()
    (root / anchor).mkdir()
    return {
        "id": game_id,
        "path": str(root),
        "build_id": "one",
        "adapter_config": {"legacy_root": anchor, "legacy_mode": "replacement"},
        "requirements": ["作者要求的依赖必须先安装"],
    }


def write_file(root, relative, content=b"original"):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return target


def mapping(game, paths):
    return plan_legacy(game, [PurePosixPath(item) for item in paths], Path(game["path"]))


@pytest.mark.parametrize("game_id,anchor", TITLES)
@pytest.mark.parametrize("wrapper", ["", "My MOD/"])
def test_existing_resource_roundtrip_for_every_legacy_title(tmp_path, game_id, anchor, wrapper):
    game = make_game(tmp_path, game_id, anchor)
    root = Path(game["path"])
    relative = f"{anchor}/arc/player.arc" if anchor != "BIO4" else "BIO4/snd/weapon.xwb"
    target = write_file(root, relative)
    staging = tmp_path / "staging"
    staging.mkdir()
    source = wrapper + relative
    write_file(staging, source, b"modded")
    plan = mapping(game, [source])
    assert plan["blocked_reason"] is None
    assert plan["files"] == [{"source": source, "target": relative}]
    assert plan["warnings"]
    assert "作者要求的依赖必须先安装" in plan["requirements"]
    engine = Deployment(tmp_path / "state")
    prepared = engine.prepare(game, "costume", staging, plan)
    assert prepared["conflicts"] == [relative]
    mod = engine.install(game, prepared["id"], True)
    assert target.read_bytes() == b"modded"
    engine.set_enabled(game, mod["id"], False)
    assert target.read_bytes() == b"original"
    engine.set_enabled(game, mod["id"], True)
    assert target.read_bytes() == b"modded"
    engine.uninstall(game, mod["id"])
    assert target.read_bytes() == b"original"
    assert engine.list_mods(game_id) == []


def test_assets_preserve_textures_and_text_inside_anchor(tmp_path):
    game = make_game(tmp_path)
    paths = ["nativePC/arc/a.arc", "nativePC/textures/title.png", "nativePC/text/lang.txt"]
    for path in paths:
        write_file(Path(game["path"]), path)
    plan = mapping(game, [*paths, "README.md", "modinfo.ini", "showcase.png"])
    assert plan["blocked_reason"] is None
    assert [item["target"] for item in plan["files"]] == paths


def test_wrapper_metadata_is_ignored_but_unrelated_assets_are_not(tmp_path):
    game = make_game(tmp_path)
    write_file(Path(game["path"]), "nativePC/arc/a.arc")
    plan = mapping(game, ["Costume/nativePC/arc/a.arc", "Costume/README.txt"])
    assert plan["blocked_reason"] is None
    for extra in ["unrelated.png", "Costume/extra.png", "optional/README.txt"]:
        blocked = mapping(game, ["Costume/nativePC/arc/a.arc", extra])
        assert blocked["files"] == []
        assert blocked["blocked_reason"]


@pytest.mark.parametrize(
    "paths",
    [
        ["arc/a.arc"],
        ["First/nativePC/arc/a.arc", "Second/nativePC/arc/a.arc"],
        ["Options/A/nativePC/arc/a.arc"],
        ["nativePC/arc/a.arc", "nativePC_MT/arc/a.arc"],
        ["nativePC/arc/a.arc", "natives/x64/a.mesh.123"],
        ["nativePC/arc/a.arc", "reframework/autorun/a.lua"],
        ["nativePC/arc/a.arc", "installer.exe"],
        ["nativePC/arc/a.arc", "scripts/setup.bat"],
        ["nativePC/arc/a.arc", "dinput8.dll"],
        ["nativePC/arc/a.arc", "nativePC/arc/A.arc"],
        ["nativePC/arc/a.arc", "nativePC/arc/setup.exe"],
        ["nativePC/arc/a.arc", "nativePC/arc/patch.asi"],
        ["nativePC/arc/a.arc", "nativePC/arc/patch.lua"],
        ["nativePC/arc/a.arc", "nativePC/.hidden/a.arc"],
        ["nativePC/arc/a.arc", "nativePC/../escape.arc"],
    ],
)
def test_ambiguous_missing_anchor_and_executable_layouts_are_blocked(tmp_path, paths):
    game = make_game(tmp_path)
    write_file(Path(game["path"]), "nativePC/arc/a.arc")
    plan = mapping(game, paths)
    assert plan["blocked_reason"]
    assert plan["files"] == []


@pytest.mark.parametrize("game_id,anchor", TITLES)
def test_never_creates_new_unknown_resource_paths(tmp_path, game_id, anchor):
    game = make_game(tmp_path, game_id, anchor)
    plan = mapping(game, [f"{anchor}/arc/unknown.arc"])
    assert plan["blocked_reason"]
    assert not plan["files"]


@pytest.mark.parametrize(
    "game_id,anchor",
    [("residentevil42023", "BIO4"), ("residentevil7", "nativePC"), ("unknown", "nativePC")],
)
def test_known_game_identity_is_required(tmp_path, game_id, anchor):
    game = make_game(tmp_path, game_id, anchor)
    write_file(Path(game["path"]), f"{anchor}/arc/a.arc")
    assert mapping(game, [f"{anchor}/arc/a.arc"])["blocked_reason"]


@pytest.mark.parametrize(
    "config",
    [{}, {"legacy_root": "nativePC_MT"}, {"legacy_root": "nativePC", "legacy_mode": "all"}],
)
def test_configuration_must_match_trusted_game_rules(tmp_path, config):
    game = make_game(tmp_path)
    game = {**game, "adapter_config": config}
    assert mapping(game, ["nativePC/arc/a.arc"])["blocked_reason"]


def test_installed_linux_casing_is_preserved_per_segment(tmp_path):
    game = make_game(tmp_path, anchor="NativePC")
    game = {**game, "adapter_config": {"legacy_root": "nativePC", "legacy_mode": "replacement"}}
    write_file(Path(game["path"]), "NativePC/ARC/DX9/uPlayer.ARC")
    plan = mapping(game, ["nativepc/arc/dx9/uplayer.arc"])
    assert plan["blocked_reason"] is None
    assert plan["files"][0]["target"] == "NativePC/ARC/DX9/uPlayer.ARC"


@pytest.mark.parametrize("kind", ["anchor", "parent", "file"])
def test_symlink_targets_are_blocked_without_reading_outside(tmp_path, kind):
    game = make_game(tmp_path)
    root = Path(game["path"])
    outside = tmp_path / "outside"
    outside.mkdir()
    write_file(outside, "a.arc", b"private")
    if kind == "anchor":
        (root / "nativePC").rmdir()
        (root / "nativePC").symlink_to(outside, target_is_directory=True)
        source = "nativePC/a.arc"
    elif kind == "parent":
        (root / "nativePC/arc").symlink_to(outside, target_is_directory=True)
        source = "nativePC/arc/a.arc"
    else:
        (root / "nativePC/a.arc").symlink_to(outside / "a.arc")
        source = "nativePC/a.arc"
    assert mapping(game, [source])["blocked_reason"]
    assert (outside / "a.arc").read_bytes() == b"private"


def test_case_ambiguity_is_rejected_at_file_or_directory(tmp_path):
    game = make_game(tmp_path)
    root = Path(game["path"])
    write_file(root, "nativePC/arc/a.arc")
    write_file(root, "nativePC/arc/A.arc")
    # macOS commonly uses a case-insensitive test filesystem.
    if len(list((root / "nativePC/arc").iterdir())) != 2:
        pytest.skip("requires a case-sensitive filesystem")
    assert mapping(game, ["nativePC/arc/a.arc"])["blocked_reason"]


@pytest.mark.parametrize("packed", ["pl00.udas.lfs", "pl00.udas.yz2.lfs"])
def test_re4_loose_assets_requiring_packed_archive_invalidation_are_blocked(tmp_path, packed):
    game = make_game(tmp_path, "residentevil4", "BIO4")
    root = Path(game["path"])
    write_file(root, "BIO4/Em/pl00.udas")
    write_file(root, "BIO4/Em/" + packed)
    plan = mapping(game, ["BIO4/Em/pl00.udas"])
    assert plan["blocked_reason"]
    assert "LFS" in plan["blocked_reason"]


def test_re4_exact_packed_resource_replacements_do_not_rename_or_delete_files(tmp_path):
    game = make_game(tmp_path, "residentevil4", "BIO4")
    root = Path(game["path"])
    write_file(root, "BIO4/ImagePackHD/01000000.pack.yz2.lfs")
    plan = mapping(game, ["BIO4/ImagePackHD/01000000.pack.yz2.lfs"])
    assert plan["blocked_reason"] is None
    assert any("LFS" in warning for warning in plan["warnings"])
    assert any("Bin32" in requirement for requirement in plan["requirements"])


def test_re5_does_not_guess_between_old_and_gold_directories(tmp_path):
    game = make_game(tmp_path, "residentevil5", "nativePC_MT")
    root = Path(game["path"])
    write_file(root, "nativePC_MT/arc/a.arc")
    write_file(root, "nativePC/arc/a.arc")
    assert mapping(game, ["nativePC/arc/a.arc"])["blocked_reason"]


def test_missing_game_anchor_and_empty_archives_are_blocked(tmp_path):
    game = make_game(tmp_path)
    (Path(game["path"]) / "nativePC").rmdir()
    assert mapping(game, ["nativePC/arc/a.arc"])["blocked_reason"]
    assert mapping(game, ["README.md"])["blocked_reason"]
    assert mapping(game, [])["blocked_reason"]
