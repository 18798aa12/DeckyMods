"""Exercise the packaged backend in disposable fixtures, never real game directories."""

import ctypes.util
import json
import platform
import sys
import tempfile
import threading
import zipfile
from pathlib import Path


def smoke(plugin: Path) -> None:
    sys.path.insert(0, str(plugin / "py_modules"))
    import libarchive
    from decky_mods.adapters import plan_files
    from decky_mods.archive import extract_archive
    from decky_mods.catalog import load_catalog
    from decky_mods.deployment import Deployment
    from decky_mods.steam import SteamDiscovery

    catalog = load_catalog(plugin)
    with tempfile.TemporaryDirectory(prefix="deckymods-smoke-") as temporary:
        root = Path(temporary)
        home = root / "home"
        library = home / ".local/share/Steam"
        game_path = library / "steamapps/common/StellarBlade"
        (game_path / "SB/Content/Paks").mkdir(parents=True)
        (library / "steamapps/appmanifest_3489700.acf").write_text(
            '"AppState" { "appid" "3489700" "installdir" "StellarBlade" '
            '"buildid" "123" "StateFlags" "4" }'
        )
        game = SteamDiscovery(catalog, home).resolve("stellarblade")
        source = root / "mod.zip"
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("Example.pak", b"synthetic pak bytes")
        extracted = root / "unpacked"
        extract_archive(source, extracted, cancel=threading.Event())
        engine = Deployment(root / "state")
        plan = engine.prepare(game, "Smoke fixture", extracted, plan_files(game, extracted))
        mod = engine.install(game, plan["id"])
        target = game_path / "SB/Content/Paks/~mods/Example.pak"
        assert target.read_bytes() == b"synthetic pak bytes"
        engine.set_enabled(game, mod["id"], False)
        assert not target.exists()
        engine.set_enabled(game, mod["id"], True)
        engine.uninstall(game, mod["id"])
        assert not target.exists()

        def crash(index: int, target: str) -> None:
            raise KeyboardInterrupt("simulated interruption")

        retry = engine.prepare(game, "Interrupted fixture", extracted, plan_files(game, extracted))
        engine.fault = crash
        try:
            engine.install(game, retry["id"])
        except KeyboardInterrupt:
            pass
        restarted = Deployment(root / "state")
        restarted.recover(game)
        assert not target.exists()
        assert not restarted.db.pending(game["id"])
        # Real libarchive 7z writer/reader, rather than a renamed ZIP fixture.
        seven = root / "mod.7z"
        with libarchive.file_writer(str(seven), "7zip") as archive:
            archive.add_files(str(extracted / "Example.pak"), pathname="Other.pak")
        assert extract_archive(seven, root / "seven") == ["Other.pak"]
    print(
        json.dumps(
            {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "libarchive": ctypes.util.find_library("archive"),
                "titles": len(catalog),
                "series": len({game["series"] for game in catalog}),
                "fixtures": (
                    "ZIP+7z, Steam discovery, install/toggle/uninstall, crash recovery passed"
                ),
                "real_game_validation": False,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    smoke(Path(sys.argv[1]).resolve())
