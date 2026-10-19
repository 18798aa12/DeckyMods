"""Validate a built plugin's layout, metadata, public methods and privacy boundaries."""

import ast
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

from scripts.sanitize import check


def verify(path: Path) -> None:
    check(path)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate distribution members")
        for item in archive.infolist():
            name = PurePosixPath(item.filename)
            if name.parts[0] != "DeckyMods" or item.file_size > 32 * 1024**2:
                raise ValueError("Unexpected ZIP member")
            if (item.external_attr >> 16) & 0o170000 != 0o100000:
                raise ValueError("Non-regular ZIP member")
        required = {
            "main.py",
            "plugin.json",
            "package.json",
            "dist/index.js",
            "LICENSE",
            "README.md",
            "THIRD_PARTY_NOTICES.md",
            "data/games.json",
            "assets/update-allowed-signers",
            "py_modules/libarchive/__init__.py",
            "py_modules/libarchive/ffi.py",
            "py_modules/decky_mods/service.py",
            "py_modules/decky_mods/nxm_helper.py",
            "licenses/libarchive-c-LICENSE",
            "licenses/decky-api-LICENSE",
            "licenses/react-icons-LICENSE",
            "licenses/tslib-LICENSE",
        }
        if not {"DeckyMods/" + name for name in required} <= set(names):
            raise ValueError("Incomplete plugin ZIP")
        plugin = json.loads(archive.read("DeckyMods/plugin.json"))
        package = json.loads(archive.read("DeckyMods/package.json"))
        if "remote_binary" in package and package["remote_binary"] != []:
            raise ValueError("Release must not request unsigned remote binaries")
        if plugin["name"] != "DeckyMods" or plugin["flags"] != [] or plugin["api_version"] != 1:
            raise ValueError("Unexpected permission/API metadata")
        games = json.loads(archive.read("DeckyMods/data/games.json"))
        if len({game["series"] for game in games}) < 50:
            raise ValueError("Insufficient distinct series catalog")
        tree = ast.parse(archive.read("DeckyMods/main.py"))
        methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)}
        if (
            not {"_main", "_unload", "get_import_directory", "install_plan", "accept_nxm"}
            <= methods
        ):
            raise ValueError("Missing lifecycle/RPC methods")
        for name in names:
            if name.endswith(".py"):
                compile(archive.read(name), name, "exec")
    print(f"Verified {path.name}: complete user-mode plugin, syntax and privacy checks passed")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
