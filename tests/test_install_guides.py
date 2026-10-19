"""Researched routes cannot become write permissions from mutable catalog hints."""

import json

import pytest
from decky_mods.errors import ModsError
from decky_mods.install_guides import InstallGuides


def write_guides(root, games):
    (root / "data").mkdir(exist_ok=True)
    (root / "data/install_guides.json").write_text(
        json.dumps({"schema_version": 1, "checked_at": "2026-10-19", "games": games})
    )


def guide():
    return {
        "game_id": "stardewvalley",
        "name": "Stardew Valley",
        "steam_app_ids": ["413150"],
        "checked_at": "2026-10-19",
        "notes": ["Separate runtime versions"],
        "sources": ["https://github.com/Pathoschild/SMAPI"],
        "methods": [
            {
                "id": "manual-test",
                "label": "External framework",
                "versions": ["1.6"],
                "format": "custom",
                "destination": "external tool",
                "requirements": [],
                "source_urls": ["https://github.com/Pathoschild/SMAPI"],
                "can_install": True,
                "install_mode": "method:manual-test",
            }
        ],
        "upstream": [],
    }


def test_only_reviewed_methods_can_grant_install_modes_and_results_are_copies(tmp_path):
    write_guides(tmp_path, [guide()])
    registry = InstallGuides(tmp_path)
    game = {
        "id": "steam-413150",
        "name": "Old identity",
        "steam_app_ids": ["413150"],
        "app_id": "413150",
    }
    result = registry.for_game(game)
    assert result["game_id"] == game["id"]
    assert next(m for m in result["methods"] if m["id"] == "manual-test")["can_install"] is False
    result["notes"].append("modified")
    assert "modified" not in registry.for_game(game)["notes"]
    assert registry.resolve_mode(game, "method:profile-smapi") == "smapi"
    with pytest.raises(ModsError):
        registry.resolve_mode(game, "method:manual-test")
    with pytest.raises(ModsError):
        registry.resolve_mode({"id": "other", "steam_app_ids": ["42"]}, "method:profile-smapi")


def test_duplicate_appid_evidence_is_rejected(tmp_path):
    write_guides(tmp_path, [guide(), {**guide(), "game_id": "another"}])
    with pytest.raises(ModsError):
        InstallGuides(tmp_path).for_game({"id": "stardewvalley", "steam_app_ids": ["413150"]})


def test_unresearched_games_have_no_install_permissions(tmp_path):
    write_guides(tmp_path, [guide()])
    assert (
        InstallGuides(tmp_path).for_game({"id": "other", "name": "Other", "steam_app_ids": ["42"]})[
            "methods"
        ]
        == []
    )


def test_corrupt_or_linked_guides_fail_closed(tmp_path):
    write_guides(tmp_path, [guide()])
    (tmp_path / "data/install_guides.json").write_text("{}")
    with pytest.raises(ModsError):
        InstallGuides(tmp_path).for_game({"id": "other"})


def test_deeply_nested_corrupt_guides_fail_with_actionable_safe_error(tmp_path):
    write_guides(tmp_path, [guide()])
    (tmp_path / "data/install_guides.json").write_text("[" * 1500 + "0" + "]" * 1500)
    with pytest.raises(ModsError, match="重新安装"):
        InstallGuides(tmp_path).for_game({"id": "other"})
