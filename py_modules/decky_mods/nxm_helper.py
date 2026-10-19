"""Standalone, standard-library-only nxm protocol receiver. Never prints signed URIs."""

import argparse
import json
import os
import re
import stat
import sys
import tempfile
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit

ENTRY = re.compile(r"[a-f0-9]{32}\.json\Z")
MAX_URI = 8192
MAX_ENTRY = 16384
MAX_QUEUE = 64


def _private_queue(queue: Path) -> None:
    queue.mkdir(parents=True, exist_ok=True, mode=0o700)
    info = queue.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise ValueError("Unsafe queue")
    queue.chmod(0o700)


def enqueue(queue: Path, uri: str) -> None:
    """Persist one browser handoff in a bounded private inbox, including when Decky is closed."""
    if (
        len(uri.encode("utf-8")) > MAX_URI
        or urlsplit(uri).scheme != "nxm"
        or any(ord(c) < 32 for c in uri)
    ):
        raise ValueError("Invalid protocol input")
    _private_queue(queue)
    entries = list(queue.iterdir())
    for entry in entries:
        if ENTRY.fullmatch(entry.name):
            info = entry.lstat()
            if stat.S_ISREG(info.st_mode) and time.time() - info.st_mtime > 3600:
                entry.unlink()
    if sum(1 for entry in queue.iterdir() if ENTRY.fullmatch(entry.name)) >= MAX_QUEUE:
        raise ValueError("Queue full")
    target = queue / (uuid.uuid4().hex + ".json")
    fd, name = tempfile.mkstemp(prefix=".receiving-", dir=queue)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump({"uri": uri, "created": time.time()}, output)
            output.flush()
            os.fsync(output.fileno())
        # The inbox is owner-only and each publication has a fresh random UUID.
        # Refuse even an improbable pre-existing UUID (including broken symlinks).
        # Rename exposes the complete inode with nlink == 1 in one operation;
        # publishing a hard link first lets the consumer reject a valid entry.
        if os.path.lexists(target):
            raise FileExistsError("Queue entry already exists")
        os.rename(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Receive a Nexus browser download")
    parser.add_argument("--queue", required=True)
    parser.add_argument("uri")
    args = parser.parse_args()
    try:
        enqueue(Path(args.queue), args.uri)
        return 0
    except (OSError, ValueError):
        print("Unable to queue the Nexus download. Open DeckyMods and try again.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
