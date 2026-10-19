"""Directory-descriptor confinement and checked atomic per-file replacement."""

import ctypes
import errno
import hashlib
import os
import platform
import re
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .errors import ModsError
from .objects import Objects
from .paths import relative_path


def fingerprint(game: dict) -> dict:
    path = Path(game["path"])
    if path.is_symlink() or not path.is_dir() or path.resolve() != path:
        raise ModsError("游戏目录已移动、卸载或不可用，请重新扫描游戏库")
    info = path.stat()
    return {
        "path": str(path),
        "device": info.st_dev,
        "inode": info.st_ino,
        "build": game.get("build_id"),
    }


def rename_at(parent: int, source: str, target: str, *, exchange: bool) -> None:
    library = ctypes.CDLL(None, use_errno=True)
    if platform.system() == "Linux":
        rename, flags = getattr(library, "renameat2", None), 2 if exchange else 1
    elif platform.system() == "Darwin":
        rename, flags = getattr(library, "renameatx_np", None), 2 if exchange else 4
    else:
        rename, flags = None, 0
    if rename is None:
        raise ModsError("当前文件系统不支持安全原子部署")
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(parent, os.fsencode(source), parent, os.fsencode(target), flags) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))


class GameFiles:
    def __init__(self, game: dict, objects: Objects, *, expected: dict | None = None):
        self.game = game
        self.objects = objects
        actual = fingerprint(game)
        self.expected = expected or actual
        if any(actual[key] != self.expected[key] for key in ("path", "device", "inode")):
            raise ModsError("游戏目录身份已变化，已停止部署")

    @contextmanager
    def parent(self, target: str, *, create: bool = False) -> Iterator[tuple[int, str]]:
        parts = relative_path(target).split("/")
        descriptor = os.open(self.game["path"], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            identity = os.fstat(descriptor)
            if (identity.st_dev, identity.st_ino) != (
                self.expected["device"],
                self.expected["inode"],
            ):
                raise ModsError("游戏目录身份已变化，拒绝写入替换后的目录")
            for part in parts[:-1]:
                if create:
                    try:
                        os.mkdir(part, 0o755, dir_fd=descriptor)
                        os.fsync(descriptor)
                    except FileExistsError:
                        pass
                next_fd = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor
                )
                os.close(descriptor)
                descriptor = next_fd
            yield descriptor, parts[-1]
        except OSError as error:
            if error.errno in (errno.ELOOP, errno.ENOTDIR):
                raise ModsError("游戏目标含符号链接或非目录，已拒绝越界写入") from error
            raise
        finally:
            os.close(descriptor)

    @staticmethod
    def hash_at(parent: int, name: str) -> str | None:
        try:
            descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        except FileNotFoundError:
            return None
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ModsError("游戏目标不是普通文件")
            return hashlib.file_digest(stream, "sha256").hexdigest()

    def capture(self, target: str) -> tuple[str | None, int]:
        try:
            with self.parent(target) as (parent, name):
                descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
                with os.fdopen(descriptor, "rb") as stream:
                    info = os.fstat(stream.fileno())
                    if not stat.S_ISREG(info.st_mode):
                        raise ModsError("游戏目标不是普通文件")
                    digest, _ = self.objects.put(stream)
                    return digest, stat.S_IMODE(info.st_mode)
        except FileNotFoundError:
            return None, 0o644
        except OSError as error:
            raise ModsError("无法安全读取游戏目标，请检查权限和链接") from error

    def hash(self, target: str) -> str | None:
        try:
            with self.parent(target) as (parent, name):
                return self.hash_at(parent, name)
        except FileNotFoundError:
            return None
        except OSError as error:
            raise ModsError("无法安全检查游戏文件") from error

    def clean_temp(self, target: str, temporary: str, known: set[str | None]) -> None:
        with self.parent(target, create=False) as (parent, _):
            digest = self.hash_at(parent, temporary)
            if digest is not None:
                if digest not in known:
                    raise ModsError("恢复临时文件与记录不一致，已保留文件")
                os.unlink(temporary, dir_fd=parent)
                os.fsync(parent)

    def temp_hash(self, target: str, temporary: str) -> str | None:
        try:
            with self.parent(target) as (parent, _):
                return self.hash_at(parent, temporary)
        except FileNotFoundError:
            return None

    def retain_temp(self, target: str, temporary: str) -> str:
        with self.parent(target) as (parent, _):
            descriptor = os.open(temporary, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
            with os.fdopen(descriptor, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise ModsError("恢复临时文件类型无效，已保留")
                digest, _ = self.objects.put(stream)
            return digest

    def apply(
        self, target: str, before: str | None, after: str | None, mode: int, temporary: str
    ) -> None:
        if not re.fullmatch(r"\.deckymods-[a-f0-9]+(?:_r)?", temporary):
            raise ModsError("部署临时文件标识无效")
        with self.parent(target, create=after is not None) as (parent, name):
            if self.hash_at(parent, name) != before:
                raise ModsError("游戏文件被其他程序修改，已停止以避免覆盖")
            if before == after:
                return
            if after is None:
                rename_at(parent, name, temporary, exchange=False)
                if self.hash_at(parent, temporary) != before:
                    rename_at(parent, temporary, name, exchange=False)
                    raise ModsError("游戏文件在操作中被修改，已保留原内容")
                os.unlink(temporary, dir_fd=parent)
                os.fsync(parent)
                return
            source = self.objects.verify(after)
            descriptor = os.open(
                temporary,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
                dir_fd=parent,
            )
            try:
                with os.fdopen(descriptor, "wb") as output, source.open("rb") as stream:
                    while block := stream.read(1024 * 1024):
                        output.write(block)
                    output.flush()
                    os.fchmod(output.fileno(), mode & 0o777)
                    os.fsync(output.fileno())
                rename_at(parent, temporary, name, exchange=before is not None)
                if before is not None:
                    if self.hash_at(parent, temporary) != before:
                        if self.hash_at(parent, name) == after:
                            rename_at(parent, temporary, name, exchange=True)
                        raise ModsError("游戏文件在原子替换时被修改，已停止并保留文件")
                    os.unlink(temporary, dir_fd=parent)
                os.fsync(parent)
            except BaseException:
                # The journal owns cleanup after power loss or a failed swap.
                raise
