"""Copy local archives from owned user import directories using no-follow reads."""

import os
import re
import stat
import threading
from pathlib import Path

from .errors import ModsError

MAX_ARCHIVE = 10 * 1024**3


class LocalArchives:
    def __init__(self, home: Path):
        self.home = home.resolve()

    def directories(self) -> list[Path]:
        result = [
            self.home / part
            for part in ("Downloads", "Documents", "Desktop", "下载", "文档", "桌面")
        ]
        configured = [path for _, path in self._configured_directories()]
        return list(dict.fromkeys([*configured, *result]))

    def _configured_directories(self) -> list[tuple[str, Path]]:
        config = self.home / ".config/user-dirs.dirs"
        configured: list[tuple[str, Path]] = []
        try:
            if config.is_symlink() or config.stat().st_size > 32768:
                return configured
            text = config.read_text()
            for match in re.finditer(
                r'^XDG_(DOWNLOAD|DOCUMENTS|DESKTOP)_DIR="([^"\n]+)"$', text, re.MULTILINE
            ):
                raw = match[2].replace("$HOME", str(self.home))
                path = Path(raw)
                if path.is_absolute() and path.is_relative_to(self.home) and ".." not in path.parts:
                    configured.append((match[1], path))
        except (OSError, UnicodeError):
            # Optional desktop preference; the fixed directories remain available.
            pass
        return configured

    def start_directory(self) -> str:
        configured_downloads = [
            path for kind, path in self._configured_directories() if kind == "DOWNLOAD"
        ]
        candidates = [*configured_downloads, self.home / "Downloads", *self.directories()]
        for path in dict.fromkeys(candidates):
            parts = path.relative_to(self.home).parts
            ancestors = [self.home.joinpath(*parts[:index]) for index in range(1, len(parts) + 1)]
            if path.is_dir() and all(not ancestor.is_symlink() for ancestor in ancestors):
                return str(path)
        return str(self.home)

    def validate(self, value: str) -> Path:
        if not isinstance(value, str) or len(value) > 4096 or "\x00" in value:
            raise ModsError("请选择有效的本地压缩包")
        path = Path(value)
        if not path.is_absolute() or path.suffix.lower() not in {".zip", ".7z", ".rar"}:
            raise ModsError("请选择 ZIP、7z 或 RAR 压缩包")
        if not any(path.is_relative_to(root) for root in self.directories()):
            raise ModsError("压缩包须位于当前用户的下载、文档或桌面目录")
        try:
            relative = path.relative_to(self.home)
            current = self.home
            for part in relative.parts:
                if part in ("", ".", "..") or part.startswith("."):
                    raise ModsError("本地压缩包路径不能包含隐藏目录或越界路径")
                current = current / part
                if current.is_symlink():
                    raise ModsError("本地压缩包不能经过符号链接")
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_nlink != 1:
                raise ModsError("请选择当前用户拥有的普通压缩包，不能是链接")
            if info.st_size <= 0 or info.st_size > MAX_ARCHIVE:
                raise ModsError("压缩包大小必须在 0～10 GiB 之间")
            return path
        except OSError as error:
            raise ModsError("无法读取所选压缩包") from error

    def copy(self, source: Path, destination: Path, cancel: threading.Event) -> None:
        path = self.validate(str(source))
        descriptor = os.open(self.home, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            parts = path.relative_to(self.home).parts
            for part in parts[:-1]:
                next_fd = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor
                )
                os.close(descriptor)
                descriptor = next_fd
            file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=descriptor)
            with os.fdopen(file_fd, "rb") as stream, destination.open("xb") as output:
                initial = os.fstat(stream.fileno())
                if (
                    not stat.S_ISREG(initial.st_mode)
                    or initial.st_uid != os.geteuid()
                    or initial.st_nlink != 1
                ):
                    raise ModsError("压缩包类型、所有者或链接状态发生变化")
                os.fchmod(output.fileno(), 0o600)
                size = 0
                while block := stream.read(1024 * 1024):
                    if cancel.is_set():
                        raise ModsError("导入已取消")
                    size += len(block)
                    if size > MAX_ARCHIVE:
                        raise ModsError("压缩包大小超过 10 GiB 限制")
                    output.write(block)
                final = os.fstat(stream.fileno())
                if (initial.st_size, initial.st_mtime_ns, initial.st_ctime_ns) != (
                    final.st_size,
                    final.st_mtime_ns,
                    final.st_ctime_ns,
                ):
                    raise ModsError("压缩包在读取中发生变化，请下载完成后重试")
                output.flush()
                os.fsync(output.fileno())
        except OSError as error:
            raise ModsError("无法安全复制压缩包，请检查权限、下载状态和空间") from error
        finally:
            os.close(descriptor)
