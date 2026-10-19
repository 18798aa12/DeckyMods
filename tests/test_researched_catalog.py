"""Reviewed catalog expansion must preserve existing MOD ownership identities."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
# Snapshot the shipped identities and every non-AppID field. Only verified AppIDs
# may be appended: renaming an existing ID can orphan its MOD layers and backups.
LEGACY = {
    "stellarblade": {
        "apps": ["3489700"],
        "protected_sha256": "7edc9193561956393ca1340991c5f74af4caf06e63c22388d500fa4d7da630b9",
    },
    "skyrimspecialedition": {
        "apps": ["489830"],
        "protected_sha256": "87d4222c0f107cf0a7fba9b746947268540fd700314e169a9f6c9abc10063b18",
    },
    "fallout4": {
        "apps": ["377160"],
        "protected_sha256": "b353013165a407c413592ade00cfa5a48c5a486ad55b21e5819608d5695f2200",
    },
    "witcher3": {
        "apps": ["292030"],
        "protected_sha256": "967eb56695d02c20197ec5099d16c0cafee396189e3f7df8994b248e7b1f8679",
    },
    "darksouls2": {
        "apps": ["236430"],
        "protected_sha256": "5c33d254e58111d051704b2da243bf53ee9f540a8417210879dd4ca0f91583f9",
    },
    "monsterhunterworld": {
        "apps": ["582010"],
        "protected_sha256": "ee7ca52b58b39030dcae55b871e40ebbdaef9b1b5e014a70cf8e0749c8e3d106",
    },
    "devilmaycry5": {
        "apps": ["601150"],
        "protected_sha256": "8fad8238cd8c21c51b157245ce7bd3894a21d2be8664b5c50b3ba6fced158a61",
    },
    "dragonsdogma": {
        "apps": ["367500"],
        "protected_sha256": "f30dbc85d0612d7f58833f4c64bad7b873bfacc7f3a4257872e2941eee14b4d9",
    },
    "7daystodie": {
        "apps": ["251570"],
        "protected_sha256": "5fc523370bf00c9b9331a1d7dcbcb41db39228f5a2b51592bce9c33e8600c33e",
    },
    "ahatintime": {
        "apps": ["253230"],
        "protected_sha256": "12623c9bdd2ae5bc7741e0573485c031cf65da3efc6533898928a175b187f512",
    },
    "baldursgate3": {
        "apps": ["1086940"],
        "protected_sha256": "21513dc3cd4a1b53beaeae02b63b94ac67ca560ad66b88afd1e122ea3c9bff09",
    },
    "battletech": {
        "apps": ["637090"],
        "protected_sha256": "298f7894e57299d25c61a338372b5bf5c5869420e80a2805ba27234a28bbdbcc",
    },
    "bladeandsorcery": {
        "apps": ["629730"],
        "protected_sha256": "84ce686214e0af8b54620eb44119b6c0b4bddc2e9b8f2c18d6b4f1355f4a7a96",
    },
    "bloodstainedritualofthenight": {
        "apps": ["692850"],
        "protected_sha256": "c3731ceb450c30fc9118fbdee2299220cb3a160004bfabe6335cc8484c6a105c",
    },
    "codevein": {
        "apps": ["678960"],
        "protected_sha256": "61554b8bc88760e4533735318c6aa48ac43a3ecc1f48b02ec41fbe93dfa679fe",
    },
    "conanexiles": {
        "apps": ["440900"],
        "protected_sha256": "d886295cdb5f6dc6d4a066d20d3be4d42efe81e56d9fb9fa832a3462fdb05f44",
    },
    "cyberpunk2077": {
        "apps": ["1091500"],
        "protected_sha256": "ae473785d489826802e356a87db4fc1bd40d78fd7fca3d0555d6f61fb077cd25",
    },
    "darkestdungeon": {
        "apps": ["262060"],
        "protected_sha256": "05cc0b1f97f96f2d2196d2762a6300dd4b3da0969b6962745276e7986fae688a",
    },
    "dawnofman": {
        "apps": ["858810"],
        "protected_sha256": "53df67f746beaf1a88644742875c6a6f56cc2771df0707f9f6ff4ffb72bab358",
    },
    "divinityoriginalsin2": {
        "apps": ["435150"],
        "protected_sha256": "5817078b82504f41ef62b5ab637e12277966f1e2c0832ef0a6e15abdb2563889",
    },
    "dragonage": {
        "apps": ["17450"],
        "protected_sha256": "f3c7db673827157d41ea7e2c90e3d5dd79fe0fbfec512cbaf1622e3aaea7da4f",
    },
    "elex": {
        "apps": ["411300"],
        "protected_sha256": "ec7c07436707b8225a021214cec9ace81e7212f398d6b99b8795b84c796d9051",
    },
    "factorio": {
        "apps": ["427520"],
        "protected_sha256": "9a09b5d49df8006d7bf81bd798aa2827196c3695c519aeb85c1817a3522e4b33",
    },
    "gardenpaws": {
        "apps": ["840010"],
        "protected_sha256": "10c800174b6528d7efe6e531a7d01df6342b2b8b88874983f1012fda3ed028e9",
    },
    "greedfall": {
        "apps": ["606880"],
        "protected_sha256": "bf208c20c96e0bf8564c7f7b3efafecb6abed1516b75566b26b8a356bfa1798e",
    },
    "grimdawn": {
        "apps": ["219990"],
        "protected_sha256": "37b301e8a1a9e297ff52fcc78857738496892c2935ede57f36a01b756c763e02",
    },
    "grimrock": {
        "apps": ["207170"],
        "protected_sha256": "8966774ee7fb8b3929215fcb32aedae74c41d15aed0b64715cc0b71d48dad277",
    },
    "kenshi": {
        "apps": ["233860"],
        "protected_sha256": "33cb2fa3dfed3542cedf735ce3324685cc877b2248a98020e2a05173ad6ef1a3",
    },
    "kerbalspaceprogram": {
        "apps": ["220200"],
        "protected_sha256": "413a490398c0ad275fa38c28efb800cb26faa07c804c26d6cd667d1cdb8536d3",
    },
    "kingdomcomedeliverance": {
        "apps": ["379430"],
        "protected_sha256": "228a7e62903412c0d17a78c8bd73403a3cd6399709f8d8e4fbfece7fca92f8ac",
    },
    "halothemasterchiefcollection": {
        "apps": ["976730"],
        "protected_sha256": "7e38e19a53706d50703d308448ecd17a2b1c86e3ccba8c0a92dc19ed341ac600",
    },
    "microsoftflightsimulator": {
        "apps": ["1250410"],
        "protected_sha256": "1652383b90139be79bdf11be1054e69a5f0823f4029182c0fe0f4f587208dd38",
    },
    "mbwarband": {
        "apps": ["48700"],
        "protected_sha256": "c6ed7572ec38dfbe186d51b7349c51dc54d49fbe44cec9a9176b835afe0ef142",
    },
    "neverwinter": {
        "apps": ["704450"],
        "protected_sha256": "707cf6c981c43f82edadd19bad6e852d20d3062dc2175a993a03062eaf3dacea",
    },
    "nomanssky": {
        "apps": ["275850"],
        "protected_sha256": "63ec3709ccf12b30b3b1deeaf673fa9bf139c22e802e19c3357f0e72d88323c2",
    },
    "oxygennotincluded": {
        "apps": ["457140"],
        "protected_sha256": "119e4a0ea5d575e8eb9223cd70f24edebd9218329bd8794f5a50a5bbd4b0c5f9",
    },
    "palworld": {
        "apps": ["1623730"],
        "protected_sha256": "8b7e4609753028438b70f6371e785944575c7458a240b168cc4aad9eecf9b545",
    },
    "pathfinderkingmaker": {
        "apps": ["640820"],
        "protected_sha256": "cb6606408ef14de88195f2ebf31c4f5de88e9e300fab83687a7588e94ee587bf",
    },
    "prisonarchitect": {
        "apps": ["233450"],
        "protected_sha256": "ba7f38a21eb980e9986da64cb3938b03444347d5a6b5678091a63c535b10c5d6",
    },
    "rimworld": {
        "apps": ["294100"],
        "protected_sha256": "0a3339b946b5f2b91477134a7ca62db85d924d49e8128069f17cb5a21e69de13",
    },
    "sekiro": {
        "apps": ["814380"],
        "protected_sha256": "4a0137ee298d51840b89379b6a46ff0c82a01b304203fff0ac03d8d361034456",
    },
    "shadowrunreturns": {
        "apps": ["234650"],
        "protected_sha256": "147327331d3931bc5088179fcf436252ed60c6ecf0d59bc75786cfc8fdc3e46c",
    },
    "thesims3": {
        "apps": ["47890"],
        "protected_sha256": "8f63c4205c10828c0cd24536708f23151a266d404e7601b0fd6e1e5cb5160fc2",
    },
    "spyroreignitedtrilogy": {
        "apps": ["996580"],
        "protected_sha256": "b303750b2b6ac69c1241c853502247605ad83115a6130831f1734a1d631f66ba",
    },
    "starbound": {
        "apps": ["211820"],
        "protected_sha256": "97691c24e7ccb61068a7a916de503ca3c3762485af2d9516a268a61bed4e71b3",
    },
    "stardewvalley": {
        "apps": ["413150"],
        "protected_sha256": "20729ef682ca3fca4b4c270ce6b0a0418134d4c103c39932c8e9b31f4493b677",
    },
    "starfield": {
        "apps": ["1716740"],
        "protected_sha256": "1ef7a760f05590ee408788da5e96934142edc035b308cfd784bfc1687c8d594c",
    },
    "stateofdecay": {
        "apps": ["241540"],
        "protected_sha256": "329fde8a3d6890ee1b78575f65d58ed241ffdd5d69eb037c861f6175c769cfd3",
    },
    "subnautica": {
        "apps": ["264710"],
        "protected_sha256": "a1dd252f7f4e2d7eea36ac695bba76b41884f4557bdb4de1a73a872bbd58d420",
    },
    "survivingmars": {
        "apps": ["464920"],
        "protected_sha256": "efb1912690483f4a153bb91117100d9ca85a7d689bf603788adaf4336fb77e9b",
    },
    "kotor": {
        "apps": ["32370"],
        "protected_sha256": "11c952905c24e097b4aae41b648391760033a4f91e68537e8161152993e73fb3",
    },
    "teamfortress2": {
        "apps": ["440"],
        "protected_sha256": "0ab3d96a04d93d040e178fda5da88dc640e85e3ddc15f81b4d4500b61f2f54eb",
    },
    "torchlight2": {
        "apps": ["200710"],
        "protected_sha256": "c33e462e7654183182177a4a2164311ed498677b58738ae1978fa2ac8db24f7c",
    },
    "totalwarthreekingdoms": {
        "apps": ["779340"],
        "protected_sha256": "0180a867788a3aedf13c87d5b106322709a4a7e2bf01574d21b5b837538ea3d1",
    },
    "untitledgoosegame": {
        "apps": ["837470"],
        "protected_sha256": "e7a6aa0827e86bf8d8033325329b32511d0a0c345c47d385102b7061438dff62",
    },
    "vampirebloodlines": {
        "apps": ["2600"],
        "protected_sha256": "b0c8445551465b57bb4bef4371d71c9f432408c8be46e22919600718a731e2c2",
    },
    "wolcenlordsofmayhem": {
        "apps": ["424370"],
        "protected_sha256": "332a6e4a1236c64b0bcc41ea9981a61b8a803021adb1b086d969e071180442aa",
    },
    "x4foundations": {
        "apps": ["392160"],
        "protected_sha256": "ed16bd5db35f742b6c4f4c05a4adbf6aee53850f62256d9f14c294e9afb2fdd5",
    },
    "xcom2": {
        "apps": ["268500"],
        "protected_sha256": "66a13f8167687277a4c8f18313a1a2128ed915f76ffd9e1fd877a8220dc3f7d3",
    },
    "residentevil0biohazard0hdremaster": {
        "apps": ["339340"],
        "protected_sha256": "d789e80595c37e89a6b8451a3d7397eb1a940967c1bd016b3c5a94d532ac4a9f",
    },
    "residentevilbiohazardhdremaster": {
        "apps": ["304240"],
        "protected_sha256": "318a380dba155d56ce51e08e5f5d4e8b807f2ccd09ab317c5fc60c8fe336a098",
    },
    "residentevil22019": {
        "apps": ["883710"],
        "protected_sha256": "679b3a4b4d97c395a0560e52f2516c3c0cc50a2fd365e361046285c778e26122",
    },
    "residentevil32020": {
        "apps": ["952060"],
        "protected_sha256": "a46717564ad32f7e7c3e62cea570aff7b199c34b25856fd35bb0818bad941fb7",
    },
    "residentevil4": {
        "apps": ["254700"],
        "protected_sha256": "b85bcb77d59f95bbd1b0cdaee4bc117658e79413001287fa977c154b93df1369",
    },
    "residentevil42023": {
        "apps": ["2050650"],
        "protected_sha256": "9d091a5e2193ba2334230b3dd375f8b135d3f4b94d9fc7067dcf047320d72f6b",
    },
    "residentevil5": {
        "apps": ["21690"],
        "protected_sha256": "fb2fceff379f240f7f6590cfbde4476fef88afaa4374fef58bffbd9acc93b09b",
    },
    "residentevil6": {
        "apps": ["221040"],
        "protected_sha256": "5fe0193305f4c8e81a0edabfc93fd9f1835cb8ee158cec019ffed3f1c5be477c",
    },
    "residentevil7": {
        "apps": ["418370"],
        "protected_sha256": "3bfb815bafd0cb328bbd509169dd370d2b9af2dff0fdb79e66759cb71332728c",
    },
    "residentevilvillage": {
        "apps": ["1196590"],
        "protected_sha256": "9b4e9525bcd82e5ee625f853db7c967eb5eef932fe1503bf4b62f98fcfc9ba7a",
    },
    "residentevilrevelations": {
        "apps": ["222480"],
        "protected_sha256": "74e55dbf80894f3e29537fe6815cb1d98d03feb73f55b1a7d407aaf135b6964f",
    },
    "residentevilrevelations2": {
        "apps": ["287290"],
        "protected_sha256": "e9a186fcfad19f33613b6db95e23e2229264bfd22286df9e6f4273c7be706fa7",
    },
    "residentevilrequiem": {
        "apps": ["3764200"],
        "protected_sha256": "d472ccc314fcfe9a5e9318fdba901d24ed9bc1b599e7cbd402b2c9c5cfd300f3",
    },
}


def catalog() -> list[dict]:
    return json.loads((ROOT / "data/games.json").read_text())


def guides() -> dict:
    return json.loads((ROOT / "data/install_guides.json").read_text())


def test_expansion_contains_at_least_100_independent_steam_games() -> None:
    rows = catalog()
    assert len(rows) >= 100
    assert len({game["id"] for game in rows}) == len(rows)
    identities = [app for game in rows for app in game["steam_app_ids"]]
    assert len(identities) == len(set(identities)), "Same-AppID editions must share one game"
    assert all(re.fullmatch(r"[1-9][0-9]{0,9}", app) for app in identities)
    assert not {"minecraft-java", "tmodloader"} & {game["id"] for game in rows}
    assert "1281930" not in identities, "tModLoader is Terraria's loader, not another game"


def test_all_shipped_game_attributes_survive_and_appids_only_append() -> None:
    current = {game["id"]: game for game in catalog()}
    assert len(LEGACY) == 72
    assert LEGACY.keys() <= current.keys()
    for game_id, previous in LEGACY.items():
        row = current[game_id]
        assert row["steam_app_ids"][: len(previous["apps"])] == previous["apps"]
        protected = {key: value for key, value in row.items() if key != "steam_app_ids"}
        payload = json.dumps(protected, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        assert hashlib.sha256(payload.encode()).hexdigest() == previous["protected_sha256"], game_id


def test_new_catalog_recognition_does_not_grant_automatic_installation() -> None:
    for row in catalog():
        if row["id"] not in LEGACY:
            assert row["adapter"] == row["support"] == "catalog"
            assert row["adapter_config"] == {}
            assert "hardware" in row["validation"]
            assert row["requirements"] and row["sources"]


def test_research_guides_cover_100_real_catalog_games() -> None:
    document = guides()
    assert document["schema_version"] == 1
    assert document["checked_at"] == "2026-10-19"
    rows = document["games"]
    assert len(rows) >= 100
    assert len({game["game_id"] for game in rows}) == len(rows)
    actual = {game["id"]: game for game in catalog()}
    for row in rows:
        entry = actual[row["game_id"]]
        assert row["steam_app_ids"] == entry["steam_app_ids"]
        assert row["name"] == entry["name"]
        assert row["checked_at"] == document["checked_at"]
        assert row["methods"] and row["sources"] and row["notes"] and row["upstream"]


def test_manual_guides_never_become_executable_by_research_classification() -> None:
    for row in guides()["games"]:
        method_ids = [method["id"] for method in row["methods"]]
        assert len(method_ids) == len(set(method_ids)), row["game_id"]
        for method in row["methods"]:
            assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", method["id"])
            assert isinstance(method["can_install"], bool)
            if method["can_install"]:
                assert method["automation"] == "implemented_candidate"
                assert isinstance(method["install_mode"], str)
                assert method["install_mode"].startswith("profile:")
            else:
                assert method["install_mode"] is None
            assert method["versions"] and method["format"] and method["requirements"]
            assert method["source_urls"]


def test_research_keeps_both_game_branches_without_counting_editions_twice() -> None:
    by_game = {game["game_id"]: game for game in guides()["games"]}
    by_app = {app: game for game in catalog() for app in game["steam_app_ids"]}
    assert by_app["435150"]["id"] == "divinityoriginalsin2"
    dos = by_game["divinityoriginalsin2"]
    assert {"dos2-de", "dos2-classic"} <= {m["id"] for m in dos["methods"]}
    assert by_app["271590"]["id"] == by_app["3240220"]["id"] == "gta5"
    terraria = by_game[by_app["105600"]["id"]]
    assert "tmodloader-manual" in {method["id"] for method in terraria["methods"]}
    assert {"xcom2-base", "xcom2-wotc"} <= {m["id"] for m in by_game["xcom2"]["methods"]}
    assert {"nms-current", "nms-legacy-pak"} <= {m["id"] for m in by_game["nomanssky"]["methods"]}
    for game_id in ("residentevil22019", "residentevil32020", "residentevil7"):
        assert {"reframework-loader", "reframework-legacy-nonrt"} <= {
            method["id"] for method in by_game[game_id]["methods"]
        }


def test_unverified_nexus_domains_remain_empty_and_old_domains_are_preserved() -> None:
    by_app = {app: game for game in catalog() for app in game["steam_app_ids"]}
    for app in ("632360", "2881650", "1366540"):
        assert by_app[app]["nexus_domain"] == ""
    assert by_app["21690"]["nexus_domain"] == "residentevil5goldedition"
    assert by_app["435150"]["nexus_domain"] == "divinityoriginalsin2"


def test_all_research_urls_are_explicit_https_without_credentials_or_spaces() -> None:
    for row in guides()["games"]:
        urls = [*row["sources"], *(u for m in row["methods"] for u in m["source_urls"])]
        for url in urls:
            parsed = urlsplit(url)
            assert parsed.scheme == "https" and parsed.hostname
            assert not parsed.username and not parsed.password
            assert not any(character.isspace() for character in url)


def test_100_game_research_document_is_bundled_and_honest() -> None:
    document = (ROOT / "docs/INSTALL_METHODS.md").read_text()
    assert "未进行 Steam Deck 实机验证" in document
    assert "并非" in document and "全自动" in document
    for row in guides()["games"]:
        assert f"`{row['game_id']}`" in document


def test_real_registry_serves_every_catalog_game_and_keeps_research_count() -> None:
    from decky_mods.catalog import load_catalog
    from decky_mods.install_guides import InstallGuides

    registry = InstallGuides(ROOT)
    rows = load_catalog(ROOT)
    assert len(rows) == 145
    results = [registry.for_game(game) for game in rows]
    researched = [row for row in results if row["checked_at"] == "2026-10-19"]
    assert len(researched) == 113
    original_methods = [
        method
        for row in researched
        for method in row["methods"]
        if not method["id"].startswith("profile-")
    ]
    assert len(original_methods) == 244
    assert all(not method["can_install"] for method in original_methods)
    assert all(method["install_mode"] is None for method in original_methods)


def test_real_registry_method_fields_match_the_public_ui_contract() -> None:
    from decky_mods.install_guides import InstallGuides

    registry = InstallGuides(ROOT)
    for game in catalog():
        for method in registry.for_game(game)["methods"]:
            for field in ("id", "label", "format", "destination"):
                assert isinstance(method[field], str) and method[field]
            for field in ("versions", "requirements", "source_urls"):
                assert isinstance(method[field], list)
                assert all(isinstance(value, str) for value in method[field])
