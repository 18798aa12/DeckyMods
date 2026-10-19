"""Small private-file primitives shared by the Nexus integration."""

import json
import os
import stat
import tempfile
from pathlib import Path

from .errors import ModsError


def private_directory(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
            raise ModsError("Nexus 私有目录不安全，请检查文件权限")
        path.chmod(0o700)
    except OSError:
        raise ModsError("无法创建 Nexus 私有目录，请检查文件权限") from None


def read_json(path: Path, limit: int = 16384) -> dict | None:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    except OSError:
        raise ModsError("Nexus 本地设置不安全或无法读取") from None
    try:
        with os.fdopen(fd, "rb") as source:
            info = os.fstat(source.fileno())
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or info.st_size > limit
                or info.st_nlink != 1
            ):
                raise ModsError("Nexus 本地设置不安全或太大")
            os.fchmod(source.fileno(), 0o600)
            result = json.loads(source.read(limit + 1))
        if not isinstance(result, dict):
            raise ModsError("Nexus 本地设置格式无效，请重新绑定")
        return result
    except (OSError, ValueError):
        raise ModsError("Nexus 本地设置格式无效，请重新绑定") from None


def write_json(path: Path, value: dict) -> None:
    private_directory(path.parent)
    temporary: Path | None = None
    try:
        if path.is_symlink():
            raise ModsError("拒绝写入不安全的 Nexus 设置路径")
        fd, name = tempfile.mkstemp(prefix=".nexus-", dir=path.parent)
        temporary = Path(name)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(value, output, ensure_ascii=False)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    except OSError:
        raise ModsError("无法保存 Nexus 本地设置") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
