"""Stream regular archive members; no archive extraction writes paths itself."""

import os
import shutil
import stat
import threading
from pathlib import Path

from .errors import ModsError
from .paths import private_directory, relative_path

MAX_EXPANDED = 32 * 1024**3
MAX_MEMBERS = 50000


def extract_archive(
    source: Path,
    destination: Path,
    *,
    max_bytes: int = MAX_EXPANDED,
    max_files: int = MAX_MEMBERS,
    cancel: threading.Event | None = None,
) -> list[str]:
    """Reject unsafe names/links/collisions and enforce actual streamed byte limits."""
    if destination.exists() or source.is_symlink() or not source.is_file():
        raise ModsError("压缩包或新的解包目录无效")
    private_directory(destination)
    files: list[str] = []
    seen: set[str] = set()
    total = 0
    try:
        import libarchive

        descriptor = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
        with (
            os.fdopen(descriptor, "rb") as stream,
            libarchive.fd_reader(stream.fileno()) as entries,
        ):
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ModsError("压缩包不是普通文件")
            for entry in entries:
                if cancel and cancel.is_set():
                    raise ModsError("操作已取消")
                if len(seen) >= max_files:
                    raise ModsError("压缩包文件数量超过限制")
                if not isinstance(entry.pathname, str):
                    raise ModsError("压缩包文件名编码不受支持")
                name = relative_path(entry.pathname.rstrip("/") if entry.isdir else entry.pathname)
                if (
                    entry.issym
                    or entry.islnk
                    or entry.linkpath
                    or not (entry.isdir or entry.isfile)
                ):
                    raise ModsError("压缩包包含链接或特殊文件，已拒绝")
                folded = name.casefold()
                if folded in seen:
                    raise ModsError("压缩包包含重复或大小写冲突的路径")
                seen.add(folded)
                path = destination / name
                if entry.isdir:
                    path.mkdir(parents=True, exist_ok=True, mode=0o700)
                    continue
                if entry.size is not None and entry.size < 0:
                    raise ModsError("压缩包文件大小无效")
                if entry.size and total + entry.size > max_bytes:
                    raise ModsError("解包大小超过限制")
                path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                with path.open("xb") as output:
                    os.fchmod(output.fileno(), 0o600)
                    for block in entry.get_blocks():
                        if cancel and cancel.is_set():
                            raise ModsError("操作已取消")
                        total += len(block)
                        if total > max_bytes:
                            raise ModsError("解包大小超过限制")
                        output.write(block)
                files.append(name)
        if not files:
            raise ModsError("压缩包没有可安装的普通文件")
        return files
    except ModsError:
        shutil.rmtree(destination)
        raise
    except (OSError, ValueError, ImportError, UnicodeError) as error:
        shutil.rmtree(destination)
        raise ModsError("无法读取 ZIP/7z/RAR，请检查文件、密码和系统 libarchive") from error
    except Exception as error:
        # libarchive's native error can contain a private source path.
        shutil.rmtree(destination)
        raise ModsError("压缩包损坏、加密或格式不受支持") from error
