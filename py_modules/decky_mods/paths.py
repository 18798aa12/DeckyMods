"""Private durable files and portable relative paths."""

import os
import re
import stat
import tempfile
import unicodedata
from pathlib import Path

from .errors import ModsError


def relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 1024:
        raise ModsError("MOD 文件路径无效")
    value = unicodedata.normalize("NFC", value.replace("\\", "/"))
    parts = value.split("/")
    if (
        any(
            not part
            or part in (".", "..")
            or part.startswith(".")
            or ":" in part
            or any(ord(char) < 32 or ord(char) == 127 for char in part)
            or part[-1:] in (".", " ")
            or len(part.encode("utf-8")) > 255
            for part in parts
        )
        or len(parts) > 32
        or re.match(r"^[A-Za-z]:", value)
    ):
        raise ModsError("MOD 含越界、隐藏或不兼容的文件路径，已拒绝")
    return value


def private_directory(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or directory.is_symlink() or info.st_uid != os.geteuid():
        raise ModsError("插件私有目录的类型或所有者无效")
    directory.chmod(0o700)


def sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_write(path: Path, data: bytes, mode: int = 0o600) -> None:
    private_directory(path.parent)
    if path.is_symlink():
        raise ModsError("私有文件不能是符号链接")
    descriptor, temporary = tempfile.mkstemp(prefix="write-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        Path(temporary).unlink(missing_ok=True)
