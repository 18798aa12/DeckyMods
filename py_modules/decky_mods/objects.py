"""Content-addressed immutable file bytes shared by MOD layers and backups."""

import hashlib
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import BinaryIO

from .errors import ModsError
from .paths import private_directory, sync_directory


class Objects:
    def __init__(self, directory: Path):
        self.directory = directory
        private_directory(directory)

    def put(self, stream: BinaryIO) -> tuple[str, int]:
        descriptor, temporary = tempfile.mkstemp(prefix="object-", dir=self.directory)
        digest, size = hashlib.sha256(), 0
        try:
            with os.fdopen(descriptor, "wb") as output:
                while block := stream.read(1024 * 1024):
                    size += len(block)
                    if size > 32 * 1024**3:
                        raise ModsError("单个 MOD 文件超过大小限制")
                    digest.update(block)
                    output.write(block)
                output.flush()
                os.fchmod(output.fileno(), 0o400)
                os.fsync(output.fileno())
            result = digest.hexdigest()
            target = self.directory / result
            if target.exists():
                self.verify(result)
            else:
                os.replace(temporary, target)
                sync_directory(self.directory)
            return result, size
        finally:
            Path(temporary).unlink(missing_ok=True)

    def path(self, digest: str) -> Path:
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ModsError("文件备份标识损坏")
        return self.directory / digest

    def verify(self, digest: str) -> Path:
        path = self.path(digest)
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ModsError("MOD 对象或备份的类型无效")
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            if actual != digest:
                raise ModsError("MOD 对象或原文件备份校验失败，已停止操作")
            return path
        except OSError as error:
            raise ModsError("MOD 对象或原文件备份缺失，已停止操作") from error
