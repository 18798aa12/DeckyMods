"""Verified, pinned inputs and deterministic distribution file helpers."""

import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPOCH = (2024, 1, 1, 0, 0, 0)
IGNORED = {"__pycache__", ".DS_Store", ".pytest_cache", ".ruff_cache"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def files(directory: Path) -> list[Path]:
    result = []
    for path in sorted(directory.rglob("*")):
        if any(part in IGNORED for part in path.relative_to(directory).parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Release input cannot be a link: {path.name}")
        if path.is_file() and path.suffix not in {".pyc", ".pyo", ".so", ".dylib"}:
            result.append(path)
    return result


def write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
        Path(temporary).chmod(0o644)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def fetch(spec: dict, *, source: bool = False) -> Path:
    url = spec["source_url" if source else "url"]
    expected = spec["source_sha256" if source else "sha256"]
    if not url.startswith("https://files.pythonhosted.org/"):
        raise ValueError("Unreviewed build input host")
    target = ROOT / ".cache/inputs" / Path(url).name
    if target.is_file() and not target.is_symlink() and digest(target) == expected:
        return target
    request = urllib.request.Request(url, headers={"User-Agent": "DeckyMods-build/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if not response.geturl().startswith("https://files.pythonhosted.org/"):
            raise ValueError("Unreviewed build redirect")
        payload = response.read(4 * 1024**2 + 1)
    if len(payload) > 4 * 1024**2 or hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError("Build input size or SHA256 mismatch")
    write(target, payload)
    return target


def lock() -> dict:
    return json.loads((ROOT / "data/dependencies.json").read_text())
