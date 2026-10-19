"""Fail distribution checks on private settings, credentials, or signed grants."""

import re
import sys
import tarfile
import zipfile
from pathlib import Path

FORBIDDEN = {
    "settings",
    "profiles",
    "logs",
    ".env",
    ".venv",
    "node_modules",
    ".git",
    "account.json",
    "jobs.json",
    "state.sqlite3",
    "__pycache__",
}


def inspect_bytes(name: str, payload: bytes) -> None:
    text = payload.decode("utf-8", errors="ignore")
    test = name.startswith(("tests/", "DeckyMods/tests/")) or ".test." in name
    home = re.compile(r"/" + r"Users/[^\s/\"']+/")
    grant = re.compile(r"nxm://[^\s\"'<>]+[?&]key=[^\s\"'<>]+", re.I)
    key = re.compile(r"[\"'](?:api_key|apikey)[\"']\s*:\s*[\"']([A-Za-z0-9._-]{32,})")
    if re.search(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----", text):
        raise ValueError(f"Private key in {name}")
    if key.search(text) or (not test and (home.search(text) or grant.search(text))):
        raise ValueError(f"Private data or signed grant in {name}")


def inspect_member(name: str, payload: bytes) -> None:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or any(part in FORBIDDEN for part in path.parts):
        raise ValueError(f"Forbidden distribution member: {name}")
    if path.suffix in {".pyc", ".key", ".pem", ".sqlite3", ".log"}:
        raise ValueError(f"Private/generated member: {name}")
    inspect_bytes(name, payload)


def check(path: Path) -> None:
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as archive:
            for item in archive.infolist():
                if item.is_dir():
                    continue
                if (item.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlink in ZIP")
                inspect_member(item.filename, archive.read(item))
    else:
        with tarfile.open(path, "r:gz") as archive:
            for item in archive.getmembers():
                if not item.isfile():
                    raise ValueError("Non-file source member")
                stream = archive.extractfile(item)
                if stream is None:
                    raise ValueError("Unreadable source member")
                inspect_member(item.name, stream.read())


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        check(Path(argument))
    print("Distribution privacy checks passed")
