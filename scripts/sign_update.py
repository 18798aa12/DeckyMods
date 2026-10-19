"""Sign a local release manifest; the private release key never enters distribution."""

import argparse
import json
import subprocess
from pathlib import Path

from scripts.build_common import ROOT, digest
from scripts.verify_release import verify


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True, type=Path)
    args = parser.parse_args()
    version = json.loads((ROOT / "package.json").read_text())["version"]
    package = ROOT / "release" / f"DeckyMods-v{version}.zip"
    verify(package)
    raw = json.dumps(
        {
            "schema": 1,
            "version": version,
            "size": package.stat().st_size,
            "sha256": digest(package),
            "filename": package.name,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    signature = subprocess.run(
        [
            "/usr/bin/ssh-keygen",
            "-Y",
            "sign",
            "-f",
            str(args.key.resolve()),
            "-n",
            "deckymods-update",
        ],
        input=raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=10,
        check=True,
    ).stdout
    if not signature.startswith(b"-----BEGIN SSH SIGNATURE-----"):
        raise ValueError("Signature unavailable")
    (ROOT / "release/update.json").write_bytes(raw)
    (ROOT / "release/update.json.sig").write_bytes(signature)
    print(f"Signed DeckyMods {version}; private key was not copied")


if __name__ == "__main__":
    main()
