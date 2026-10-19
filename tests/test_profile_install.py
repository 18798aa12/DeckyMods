"""Reviewed archive layouts remain relative, explicit and reversible."""

import json

import pytest
from decky_mods.deployment import Deployment
from decky_mods.profile_install import plan_profile


def put(root, path, payload=b"fixture"):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)


@pytest.fixture
def layout(tmp_path):
    root, unpacked = tmp_path / "Game", tmp_path / "unpacked"
    root.mkdir()
    unpacked.mkdir()
    return (
        {
            "id": "example",
            "path": str(root),
            "installed": True,
            "running": False,
            "build_id": "1",
            "requirements": [],
        },
        root,
        unpacked,
    )


@pytest.mark.parametrize(
    "handler,source,target,marker",
    [
        (
            "cyberpunk_archive",
            "archive/pc/mod/example.archive",
            "archive/pc/mod/example.archive",
            None,
        ),
        ("cyberpunk_archive", "example.archive", "archive/pc/mod/example.archive", None),
        (
            "witcher3_mods",
            "Mods/modExample/content/test.bundle",
            "Mods/modExample/content/test.bundle",
            None,
        ),
        ("bethesda_data", "Data/Example.esp", "Data/Example.esp", None),
        ("bethesda_data", "textures/armor/test.dds", "Data/textures/armor/test.dds", None),
        (
            "bepinex_plugins",
            "BepInEx/plugins/Example/main.dll",
            "BepInEx/plugins/Example/main.dll",
            "BepInEx/core/BepInEx.dll",
        ),
    ],
)
def test_supported_profile_deploys_toggles_and_uninstalls(
    layout, tmp_path, handler, source, target, marker
):
    game, root, unpacked = layout
    if handler == "bethesda_data":
        game = {**game, "id": "skyrimspecialedition", "steam_app_ids": ["489830"]}
    if marker:
        put(root, marker)
    put(unpacked, source, b"modded")
    mapping = plan_profile(game, unpacked, handler)
    assert mapping["blocked_reason"] is None, mapping
    assert mapping["files"] == [{"source": source, "target": target}]
    assert mapping["warnings"]
    engine = Deployment(tmp_path / "state")
    plan = engine.prepare(game, "Fixture", unpacked, mapping)
    mod = engine.install(game, plan["id"])
    assert (root / target).read_bytes() == b"modded"
    engine.set_enabled(game, mod["id"], False)
    assert not (root / target).exists()
    engine.set_enabled(game, mod["id"], True)
    engine.uninstall(game, mod["id"])
    assert not (root / target).exists()


def test_smapi_validates_manifest_and_keeps_content_pack_directory(layout):
    game, root, unpacked = layout
    put(root, "StardewModdingAPI.dll")
    manifest = {
        "Name": "Pack",
        "Version": "1.0",
        "UniqueID": "Example.Pack",
        "ContentPackFor": {"UniqueID": "Pathoschild.ContentPatcher"},
    }
    put(unpacked, "Pack/manifest.json", json.dumps(manifest).encode())
    put(unpacked, "Pack/content.json", b"{}")
    mapping = plan_profile(game, unpacked, "smapi")
    assert mapping["blocked_reason"] is None
    assert {row["target"] for row in mapping["files"]} == {
        "Mods/Pack/manifest.json",
        "Mods/Pack/content.json",
    }


@pytest.mark.parametrize("handler", ["smapi", "bepinex_plugins"])
def test_required_loader_is_not_inferred_from_archive(layout, handler):
    game, _, unpacked = layout
    put(unpacked, "BepInEx/plugins/test.dll")
    assert plan_profile(game, unpacked, handler)["blocked_reason"]


@pytest.mark.parametrize(
    "unsafe",
    [
        "fomod/ModuleConfig.xml",
        "install.sh",
        "setup.exe",
        "Data/../escape",
        "Optional A/test.archive",
    ],
)
def test_profiles_refuse_unsupported_or_ambiguous_layout(layout, unsafe):
    game, _, unpacked = layout
    put(unpacked, "one.archive")
    put(unpacked, unsafe)
    result = plan_profile(game, unpacked, "cyberpunk_archive")
    assert result["blocked_reason"]
    assert result["files"] == []


def test_target_casing_uses_existing_directories_and_rejects_symlinks(layout, tmp_path):
    game, root, unpacked = layout
    game = {**game, "id": "skyrimspecialedition", "steam_app_ids": ["489830"]}
    (root / "data/Textures").mkdir(parents=True)
    put(unpacked, "textures/Test.dds")
    mapping = plan_profile(game, unpacked, "bethesda_data")
    assert mapping["files"][0]["target"] == "data/Textures/Test.dds"
    (root / "data/Textures").rmdir()
    (root / "data/Textures").symlink_to(tmp_path, target_is_directory=True)
    assert plan_profile(game, unpacked, "bethesda_data")["blocked_reason"]


def test_profile_never_mutates_a_busy_game(layout):
    game, _, unpacked = layout
    put(unpacked, "test.archive")
    assert plan_profile({**game, "updating": True}, unpacked, "cyberpunk_archive")["blocked_reason"]


def test_manifest_order_managed_games_require_their_dedicated_tool(layout):
    game, _, unpacked = layout
    put(unpacked, "Mods/Example/Data/test.pak")
    assert plan_profile(game, unpacked, "kcd_mods")["blocked_reason"]


@pytest.mark.parametrize("source", ["dinput8.dll", "RE7_TDB49/dinput8.dll"])
def test_reframework_loader_requires_explicit_external_branch_matching(layout, source):
    game, _, unpacked = layout
    put(unpacked, source)
    result = plan_profile({**game, "id": "residentevil22019"}, unpacked, "reframework_loader")
    assert result["blocked_reason"]
    assert result["files"] == []


@pytest.mark.parametrize(
    "identity,source",
    [
        ({"id": "fallout4", "steam_app_ids": ["377160"]}, "SkyrimSE/Data/SKSE/Plugins/mod.dll"),
        ({"id": "fallout4"}, "Skyrim Special Edition/Data/example.esp"),
        ({"id": "fallout4"}, "Starfield/Data/example.esp"),
        ({"id": "skyrimspecialedition"}, "Data/F4SE/Plugins/mod.dll"),
        ({"id": "oblivion"}, "Data/NVSE/Plugins/mod.dll"),
        ({"id": "fallout3"}, "Data/OBSE/Plugins/mod.dll"),
        ({"id": "skyrim"}, "Data/example.ba2"),
        ({"id": "fallout4"}, "Data/example.bsa"),
        ({"id": "fallout3"}, "Data/example.esl"),
        ({"id": "morrowind"}, "Data/example.esp"),
        ({"id": "starfield", "steam_app_ids": ["1716740"]}, "Data/example.ba2"),
        ({"id": "example"}, "Data/example.esp"),
        ({"id": "fallout4", "steam_app_ids": ["489830"]}, "Data/example.esp"),
    ],
)
def test_bethesda_rejects_unreviewed_or_explicitly_wrong_game_payload(layout, identity, source):
    game, _, unpacked = layout
    put(unpacked, source)
    result = plan_profile({**game, **identity}, unpacked, "bethesda_data")
    assert result["blocked_reason"], result
    assert result["files"] == []


@pytest.mark.parametrize(
    "identity,source",
    [
        ({"id": "skyrimspecialedition"}, "Data/SKSE/Plugins/mod.dll"),
        ({"id": "skyrim"}, "Data/example.bsa"),
        ({"id": "skyrimvr"}, "Data/textures/mod.dds"),
        ({"id": "fallout3"}, "Data/FOSE/Plugins/mod.dll"),
        ({"id": "falloutnv"}, "Data/NVSE/Plugins/mod.dll"),
        ({"id": "fallout4"}, "Data/example.ba2"),
        ({"id": "oblivion"}, "Data/OBSE/Plugins/mod.dll"),
        ({"id": "steam-377160", "steam_app_ids": ["377160"]}, "Data/example.ba2"),
    ],
)
def test_bethesda_reviewed_identity_keeps_valid_data_files(layout, identity, source):
    game, _, unpacked = layout
    put(unpacked, source)
    result = plan_profile({**game, **identity}, unpacked, "bethesda_data")
    assert result["blocked_reason"] is None, result
    assert result["files"] == [{"source": source, "target": source}]


def test_smapi_json_comments_preserve_strings_and_manifest_bytes(layout):
    game, root, unpacked = layout
    put(root, "StardewModdingAPI.dll")
    raw = b"""{
      // comment before identity
      "Name": "Pack // text", "Version": "1.0", "UniqueID": "Example.Pack",
      "Description": "https://example.invalid/a/*not-comment*/",
      /* a block comment */ "ContentPackFor": {"UniqueID": "Example.Framework"}
    }"""
    put(unpacked, "Pack/manifest.json", raw)
    put(unpacked, "Pack/content.json", b"{}")
    result = plan_profile(game, unpacked, "smapi")
    assert result["blocked_reason"] is None, result
    assert (unpacked / "Pack/manifest.json").read_bytes() == raw
    assert len(result["files"]) == 2


@pytest.mark.parametrize(
    "raw",
    [
        '{"Name":"Pack","Name":"Other","Version":"1","UniqueID":"Example.Pack",'
        '"ContentPackFor":{"UniqueID":"Example.Framework"}}',
        '{"Name":"Pack","Version":"1","UniqueID":"Example.Pack",'
        '"ContentPackFor":{"UniqueID":"Example.A","UniqueID":"Example.B"}}',
        '{"Name":"Pack","Version":"1","UniqueID":"Example.Pack",'
        '"ContentPackFor":{"UniqueID":"Example.Framework"}} /* unterminated',
    ],
)
def test_smapi_refuses_duplicate_keys_and_incomplete_comments(layout, raw):
    game, root, unpacked = layout
    put(root, "StardewModdingAPI.dll")
    put(unpacked, "Pack/manifest.json", raw.encode())
    result = plan_profile(game, unpacked, "smapi")
    assert result["blocked_reason"]
    assert result["files"] == []


def test_smapi_manifest_declares_specific_unverified_prerequisites(layout):
    game, root, unpacked = layout
    put(root, "StardewModdingAPI.dll")
    manifest = {
        "Name": "Pack",
        "Version": "1",
        "UniqueID": "Example.Pack",
        "MinimumApiVersion": "4.5.2",
        "MinimumGameVersion": "1.6.15",
        "ContentPackFor": {"UniqueID": "Example.Framework", "MinimumVersion": "2.0"},
        "Dependencies": [
            {"UniqueID": "Example.Required", "MinimumVersion": "3.0"},
            {"UniqueID": "Example.Optional", "IsRequired": False},
        ],
    }
    put(unpacked, "Pack/manifest.json", json.dumps(manifest).encode())
    result = plan_profile({**game, "requirements": ["existing requirement"]}, unpacked, "smapi")
    assert result["blocked_reason"] is None, result
    prerequisites = "\n".join(result["requirements"])
    for expected in (
        "existing requirement",
        "SMAPI",
        "4.5.2",
        "1.6.15",
        "Example.Framework",
        "2.0",
        "Example.Required",
        "3.0",
        "未验证",
    ):
        assert expected in prerequisites
    assert "Example.Optional" not in prerequisites


@pytest.mark.parametrize(
    "overrides",
    [
        {"EntryDll": False},
        {"EntryDll": "Pack.dll", "ContentPackFor": []},
        {"MinimumApiVersion": 4},
        {"MinimumGameVersion": "bad\nversion"},
        {"Dependencies": {}},
        {"Dependencies": [None]},
        {"Dependencies": [{"UniqueID": "Example.Dependency", "IsRequired": "false"}]},
        {"Dependencies": [{"UniqueID": "Bad/Path"}]},
        {"Dependencies": [{"UniqueID": "Example.Dependency", "MinimumVersion": []}]},
    ],
)
def test_smapi_rejects_malformed_requirement_fields(layout, overrides):
    game, root, unpacked = layout
    put(root, "StardewModdingAPI.dll")
    manifest = {
        "Name": "Pack",
        "Version": "1",
        "UniqueID": "Example.Pack",
        "ContentPackFor": {"UniqueID": "Example.Framework"},
        **overrides,
    }
    put(unpacked, "Pack/manifest.json", json.dumps(manifest).encode())
    put(unpacked, "Pack/Pack.dll")
    result = plan_profile(game, unpacked, "smapi")
    assert result["blocked_reason"]
    assert result["files"] == []
