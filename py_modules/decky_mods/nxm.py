"""Opt-in per-user nxm association with previous-manager preservation."""

import configparser
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from ._nexus_private import private_directory, read_json, write_json
from .errors import ModsError
from .nxm_helper import ENTRY, MAX_ENTRY, MAX_URI

DESKTOP_ID = "decky-mods-nxm.desktop"
MIME = "x-scheme-handler/nxm"
MARKER = "X-DeckyMods-Handler=true"
DESKTOP_NAME = re.compile(r"[A-Za-z0-9_.-]+\.desktop\Z")


def _quote_exec(value: str) -> str:
    if "\n" in value or "\r" in value or "%" in value:
        raise ModsError("NXM 安装路径包含不支持的字符")
    escaped = (
        value.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
    )
    # Desktop entry string escaping is a separate layer from Exec token escaping.
    return '"' + escaped.replace("\\", "\\\\") + '"'


class NxmHandler:
    def __init__(self, directory: Path, plugin_dir: Path, home: Path | None = None):
        self.directory = Path(directory)
        self.plugin_dir = Path(plugin_dir)
        self.home = Path.home() if home is None else Path(home)
        private_directory(self.directory)
        private_directory(self.directory / "inbox")
        self._lock = threading.RLock()
        self._state = read_json(self.directory / "handler.json") or {}
        self._mime = shutil.which("xdg-mime")

    def _supported(self) -> bool:
        return sys.platform == "linux" and os.getuid() != 0 and self._mime is not None

    def _run(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                [self._mime, *args], capture_output=True, text=True, timeout=10, check=False
            )
            if result.returncode != 0:
                raise ModsError("无法设置 NXM 关联，请在 SteamOS 桌面模式重试")
            return result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            raise ModsError("无法运行 xdg-mime，请在 SteamOS 桌面模式重试") from None

    def _query(self) -> str | None:
        name = self._run(["query", "default", MIME])
        if not name:
            return None
        if not DESKTOP_NAME.fullmatch(name):
            raise ModsError("现有 NXM 关联格式无效，请在桌面设置中检查")
        return name

    def status(self) -> dict:
        supported = self._supported()
        current = None
        message = None if supported else "NXM 接收仅支持 SteamOS/Linux 普通用户；仍可导入本地压缩包"
        if supported:
            try:
                current = self._query()
            except ModsError as error:
                message = str(error)
        previous = self._state.get("previous")
        return {
            "enabled": current == DESKTOP_ID,
            "supported": supported,
            "previous": previous if isinstance(previous, str) else None,
            "message": message,
        }

    def _applications(self) -> Path:
        configured = os.environ.get("XDG_DATA_HOME")
        data = Path(configured) if configured else self.home / ".local/share"
        if not data.is_absolute() or not data.is_relative_to(self.home):
            raise ModsError("NXM 关联必须安装在当前用户的主目录中")
        return data / "applications"

    def _desktop_text(self) -> str:
        helper = self.plugin_dir / "py_modules/decky_mods/nxm_helper.py"
        if not helper.is_file() or helper.is_symlink():
            raise ModsError("NXM 接收程序缺失，请重新安装 DeckyMods")
        executable = " ".join(
            _quote_exec(str(part))
            for part in ("/usr/bin/python3", helper, "--queue", self.directory / "inbox")
        )
        return (
            "[Desktop Entry]\nType=Application\nName=DeckyMods Nexus Receiver\n"
            f"Exec={executable} %u\nTerminal=false\nNoDisplay=true\n"
            f"MimeType={MIME};\n{MARKER}\n"
        )

    def _write_desktop(self, desktop: Path) -> None:
        contents = self._desktop_text()
        desktop.parent.mkdir(parents=True, exist_ok=True)
        if desktop.parent.is_symlink():
            raise ModsError("NXM 关联目录不安全")
        if desktop.exists() or desktop.is_symlink():
            if desktop.is_symlink() or MARKER not in desktop.read_text(encoding="utf-8"):
                raise ModsError("已有同名程序，拒绝覆盖 NXM 关联文件")
            return
        try:
            fd = os.open(desktop, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
            with os.fdopen(fd, "w", encoding="utf-8") as target:
                target.write(contents)
        except OSError:
            raise ModsError("无法写入 NXM 关联文件") from None

    def _remove_empty_default(self, applications: Path) -> None:
        """xdg-mime has no unset command; remove only our value when no predecessor existed."""
        config_root = Path(os.environ.get("XDG_CONFIG_HOME", str(self.home / ".config")))
        if not config_root.is_absolute() or not config_root.is_relative_to(self.home):
            raise ModsError("NXM 设置目录必须位于当前用户的主目录中")
        for path in (config_root / "mimeapps.list", applications / "mimeapps.list"):
            if not path.exists():
                continue
            info = path.lstat()
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or info.st_size > 1024**2
            ):
                raise ModsError("无法安全恢复 NXM 关联设置")
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            parser.optionxform = str
            try:
                parser.read(path, encoding="utf-8")
                for section in ("Default Applications", "Added Associations"):
                    value = parser.get(section, MIME, fallback=None)
                    if value is not None:
                        names = [name for name in value.split(";") if name and name != DESKTOP_ID]
                        if names:
                            parser.set(section, MIME, ";".join(names) + ";")
                        else:
                            parser.remove_option(section, MIME)
                fd, name = tempfile.mkstemp(prefix=".deckymods-", dir=path.parent)
                temporary = Path(name)
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as output:
                        parser.write(output)
                    os.replace(temporary, path)
                finally:
                    temporary.unlink(missing_ok=True)
            except (OSError, configparser.Error):
                raise ModsError("无法安全恢复 NXM 关联设置") from None

    def set_enabled(self, enabled: bool) -> dict:
        if not isinstance(enabled, bool):
            raise ModsError("NXM 开关参数无效")
        if not self._supported():
            raise ModsError("请在 SteamOS/Linux 普通用户下设置 NXM 接收")
        with self._lock:
            current = self._query()
            desktop = self._applications() / DESKTOP_ID
            if enabled:
                self._write_desktop(desktop)
                if current != DESKTOP_ID:
                    state = {"previous": current}
                    write_json(self.directory / "handler.json", state)
                    self._state = state
                    self._run(["default", DESKTOP_ID, MIME])
            else:
                if current == DESKTOP_ID:
                    previous = self._state.get("previous")
                    if (
                        isinstance(previous, str)
                        and DESKTOP_NAME.fullmatch(previous)
                        and previous != DESKTOP_ID
                    ):
                        self._run(["default", previous, MIME])
                    else:
                        self._remove_empty_default(desktop.parent)
                if desktop.exists() and not desktop.is_symlink():
                    if MARKER in desktop.read_text(encoding="utf-8"):
                        desktop.unlink()
                (self.directory / "handler.json").unlink(missing_ok=True)
                self._state = {}
            return self.status()

    def drain(self) -> list[str]:
        queue = self.directory / "inbox"
        private_directory(queue)
        result = []
        with self._lock:
            for path in sorted(queue.iterdir())[:128]:
                if not ENTRY.fullmatch(path.name):
                    continue
                try:
                    data = read_json(path, MAX_ENTRY)
                    if data is not None:
                        uri, created = data.get("uri"), data.get("created")
                        if (
                            isinstance(uri, str)
                            and len(uri.encode("utf-8")) <= MAX_URI
                            and uri.startswith("nxm://")
                            and isinstance(created, (int, float))
                            and 0 <= time.time() - created <= 3600
                        ):
                            result.append(uri)
                except ModsError:
                    # Untrusted queue input is discarded, never logged with grant tokens.
                    pass
                finally:
                    try:
                        path.unlink(missing_ok=True)
                    except OSError:
                        raise ModsError("无法删除已读取的 Nexus 下载授权") from None
        return result

    def close(self) -> None:
        """Keep the explicit association alive so the receiver also works while Decky is stopped."""
