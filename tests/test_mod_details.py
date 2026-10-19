import json

import pytest
from decky_mods.errors import ModsError
from decky_mods.mod_details import ModDetails

MOD_ID = "a" * 32
GAME = {"id": "residentevil7", "nexus_domain": "residentevil7"}
MOD = {"id": MOD_ID, "name": "Installed mod", "nexus_mod_id": None, "source_url": None}


class Nexus:
    def __init__(self):
        self.calls = []
        self.error = None

    def resolve(self, domain, reference):
        self.calls.append((domain, reference))
        if self.error:
            raise self.error
        return {
            "mod_id": 162,
            "name": "Item Unlocker",
            "author": "Author",
            "summary": "[b]Summary[/b]",
            "description": "<p>Official <strong>description</strong>.</p><script>secret()</script>",
            "version": "1.2",
            "page_url": "https://www.nexusmods.com/residentevil7/mods/162",
        }


@pytest.fixture
def details(tmp_path):
    nexus = Nexus()
    return ModDetails(tmp_path / "details", nexus), nexus


def extracted(tmp_path, contents):
    root = tmp_path / "extracted"
    root.mkdir(exist_ok=True)
    for name, value in contents.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value)
    return root


def test_capture_itemunlocker_flat_metadata_without_network(details, tmp_path):
    store, nexus = details
    root = extracted(
        tmp_path,
        {
            "ItemUnlocker/modinfo.ini": (
                "name=Item Unlocker\nversion=V1.2\nauthor=d3sc0le\n"
                "description=RE Framework mod that allows you to unlock all items in the game.\n"
            )
        },
    )
    metadata = store.capture(root, None, "ItemUnlocker-162-1-2-1751196981.zip", GAME)
    assert metadata["name"] == "Item Unlocker"
    assert metadata["author"] == "d3sc0le"
    assert metadata["version"] == "V1.2"
    store.remember(MOD_ID, metadata)
    result = store.get(GAME, MOD)
    assert result["description"].startswith("RE Framework")
    assert result["page_url"] is None
    assert result["origin"] == "local"
    assert nexus.calls == []


def test_known_nexus_identity_fetched_only_when_expanded(details, tmp_path):
    store, nexus = details
    root = extracted(tmp_path, {"readme.md": "[b]Local[/b]\n\nInstructions."})
    metadata = store.capture(root, {"mod_id": 162}, "package.zip", GAME)
    assert nexus.calls == []
    store.remember(MOD_ID, metadata)
    result = store.get(GAME, {**MOD, "nexus_mod_id": 162})
    assert nexus.calls == [("residentevil7", "162")]
    assert result["origin"] == "nexus"
    assert result["description"] == "Official description."
    assert result["summary"] == "Summary"
    assert "secret" not in json.dumps(result)
    assert result["version"] == "1.2"
    assert result["page_url"].endswith("/mods/162")


def test_network_failure_retains_local_metadata_and_safe_error(details, tmp_path):
    store, nexus = details
    root = extracted(tmp_path, {"modinfo.ini": "[Mod]\nauthor=Author\ndescription=Offline details"})
    store.remember(MOD_ID, store.capture(root, None, "package.zip", GAME))
    nexus.error = ModsError("请先绑定 Nexus 个人 API Key")
    result = store.get(GAME, {**MOD, "nexus_mod_id": 162})
    assert result["description"] == "Offline details"
    assert result["origin"] == "local"
    assert "请先绑定" in result["error"]
    assert result["page_url"].endswith("/mods/162")


def test_old_install_with_confirmed_source_url_can_fetch(details):
    result = details[0].get(
        GAME,
        {**MOD, "source_url": "https://www.nexusmods.com/residentevil7/mods/162?tab=description"},
    )
    assert result["origin"] == "nexus"
    assert details[1].calls == [("residentevil7", "162")]


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.test/residentevil7/mods/162",
        "https://www.nexusmods.com/skyrim/mods/162",
        "https://user:secret@www.nexusmods.com/residentevil7/mods/162",
        "http://www.nexusmods.com/residentevil7/mods/162",
        "https://www.nexusmods.com:444/residentevil7/mods/162",
    ],
)
def test_unknown_source_does_not_trigger_requests(details, url):
    result = details[0].get(GAME, {**MOD, "source_url": url})
    assert details[1].calls == []
    assert result["page_url"] is None
    assert result["origin"] == "unavailable"


def test_local_official_homepage_is_only_a_nexus_api_reference(details, tmp_path):
    store, nexus = details
    root = extracted(
        tmp_path,
        {
            "modinfo.ini": (
                "description=Local\nwebsite=https://www.nexusmods.com/residentevil7/mods/162\n"
            )
        },
    )
    metadata = store.capture(root, None, "package.zip", GAME)
    assert nexus.calls == []
    store.remember(MOD_ID, metadata)
    assert store.get(GAME, MOD)["origin"] == "nexus"
    assert nexus.calls == [("residentevil7", "162")]


def test_mismatched_nexus_response_keeps_local_details(details, tmp_path, monkeypatch):
    store, nexus = details
    root = extracted(tmp_path, {"readme.txt": "Keep this local text"})
    store.remember(MOD_ID, store.capture(root, None, "package.zip", GAME))
    monkeypatch.setattr(nexus, "resolve", lambda *_: {"mod_id": 999, "description": "wrong"})
    result = store.get(GAME, {**MOD, "nexus_mod_id": 162})
    assert result["description"] == "Keep this local text"
    assert result["error"]


def test_capture_ignores_symlinks_and_oversized_metadata(details, tmp_path):
    store, nexus = details
    root = extracted(tmp_path, {"modinfo.ini": "description=" + "x" * 40000})
    secret = tmp_path / "secret"
    secret.write_text("private")
    (root / "readme.txt").symlink_to(secret)
    metadata = store.capture(root, None, "package.zip", GAME)
    assert metadata is None or "private" not in json.dumps(metadata)
    assert nexus.calls == []


def test_symlinked_parent_metadata_not_followed(details, tmp_path):
    store, _ = details
    root = extracted(tmp_path, {})
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "modinfo.ini").write_text("description=private")
    (root / "wrapped").symlink_to(outside, target_is_directory=True)
    metadata = store.capture(root, None, "package.zip", GAME)
    assert metadata is None or "private" not in json.dumps(metadata)


def test_metadata_private_permissions_and_no_path_injection(details, tmp_path):
    store, _ = details
    root = extracted(tmp_path, {"readme.txt": "Details"})
    store.remember(MOD_ID, store.capture(root, None, "package.zip", GAME))
    assert store.directory.stat().st_mode & 0o777 == 0o700
    saved = store.directory / f"{MOD_ID}.json"
    assert saved.stat().st_mode & 0o777 == 0o600
    with pytest.raises(ModsError):
        store.remember("../evil", {"description": "bad"})
    assert not (tmp_path / "evil.json").exists()


def test_corrupt_metadata_does_not_disable_mod_management(details):
    store, _ = details
    (store.directory / f"{MOD_ID}.json").write_text("broken")
    result = store.get(GAME, MOD)
    assert result["origin"] == "unavailable"
    assert result["error"]


def test_wrong_game_metadata_not_reused(details, tmp_path):
    store, nexus = details
    root = extracted(tmp_path, {"readme.txt": "Wrong game's description"})
    store.remember(MOD_ID, store.capture(root, {"mod_id": 162}, "package.zip", GAME))
    result = store.get({"id": "skyrim", "nexus_domain": "skyrim"}, MOD)
    assert "Wrong game's" not in result["description"]
    assert nexus.calls == []
    assert result["error"]


def test_malicious_markup_is_plain_bounded_text(details, tmp_path):
    store, _ = details
    root = extracted(
        tmp_path,
        {
            "readme.md": (
                "[b]Title[/b]\n[img]https://tracker.invalid/x[/img]\n"
                "<iframe>bad</iframe><p>Safe &amp; sound</p>\x00\u202eevil"
            )
        },
    )
    store.remember(MOD_ID, store.capture(root, None, "package.zip", GAME))
    result = store.get(GAME, MOD)
    assert "Title" in result["description"]
    assert "Safe & sound" in result["description"]
    assert "tracker.invalid" not in result["description"]
    assert "bad" not in result["description"]
    assert "\u202e" not in result["description"]
    assert "\x00" not in result["description"]


def test_capture_absent_metadata_and_no_network(details, tmp_path):
    root = extracted(tmp_path, {"data/file.bin": "game data"})
    assert details[0].capture(root, None, "package-162.zip", GAME) is None
    result = details[0].get(GAME, MOD)
    assert result["description"] == ""
    assert result["error"] is None
    assert details[1].calls == []


def test_embedded_metadata_survives_without_independent_file(details, tmp_path):
    store, nexus = details
    root = extracted(
        tmp_path, {"modinfo.ini": "description=Saved with the transaction\nauthor=Local"}
    )
    metadata = store.capture(root, None, "package.zip", GAME)
    result = store.get(GAME, {**MOD, "details": metadata})
    assert result["description"] == "Saved with the transaction"
    assert result["author"] == "Local"
    assert result["source_url"] is None
    assert nexus.calls == []
    assert not (store.directory / f"{MOD_ID}.json").exists()


def test_embedded_metadata_preferred_over_old_cache(details, tmp_path):
    store, _ = details
    root = extracted(tmp_path, {"readme.txt": "Old description"})
    old = store.capture(root, None, "package.zip", GAME)
    store.remember(MOD_ID, old)
    result = store.get(GAME, {**MOD, "details": {**old, "description": "New description"}})
    assert result["description"] == "New description"


def test_invalid_embedded_metadata_is_safe_error(details):
    result = details[0].get(GAME, {**MOD, "details": ["bad"]})
    assert result["error"]
    assert result["origin"] == "unavailable"


def test_confirmed_source_url_is_canonical_in_both_response_fields(details):
    result = details[0].get(GAME, {**MOD, "nexus_mod_id": 162})
    assert result["source_url"] == result["page_url"]
    assert result["source_url"] == "https://www.nexusmods.com/residentevil7/mods/162"


def test_ambiguous_modinfo_does_not_attribute_one_author_to_bundle(details, tmp_path):
    root = extracted(
        tmp_path,
        {
            "one/modinfo.ini": "description=One\nauthor=Wrong person",
            "two/modinfo.ini": "description=Two\nauthor=Other person",
            "readme.txt": "Bundle instructions",
        },
    )
    metadata = details[0].capture(root, None, "bundle.zip", GAME)
    result = details[0].get(GAME, {**MOD, "details": metadata})
    assert result["author"] == ""
    assert result["description"] == "Bundle instructions"
    assert "多个" in result["error"]


def test_invalid_modinfo_falls_back_to_readme(details, tmp_path):
    root = extracted(
        tmp_path,
        {
            "modinfo.ini": "description=One\ndescription=Two",
            "readme.txt": "Fallback",
        },
    )
    metadata = details[0].capture(root, None, "bundle.zip", GAME)
    result = details[0].get(GAME, {**MOD, "details": metadata})
    assert result["description"] == "Fallback"
    assert result["error"]


def test_invalid_nexus_url_port_never_requested(details):
    result = details[0].get(
        GAME, {**MOD, "source_url": "https://www.nexusmods.com:invalid/residentevil7/mods/162"}
    )
    assert result["source_url"] is None
    assert details[1].calls == []


def test_unexpected_request_failure_retains_local_text(details, monkeypatch):
    def fail(*_):
        raise OSError("private request header")

    monkeypatch.setattr(details[1], "resolve", fail)
    result = details[0].get(GAME, {**MOD, "nexus_mod_id": 162})
    assert result["error"]
    assert "private request header" not in json.dumps(result)


def test_remember_rejects_non_object(details):
    with pytest.raises(ModsError):
        details[0].remember(MOD_ID, ["bad"])
