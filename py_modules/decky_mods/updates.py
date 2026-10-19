"""Signed update discovery and preparation; Decky's native installer owns replacement."""

import hashlib
import json
import os
import tempfile
import threading
from datetime import UTC, datetime
from pathlib import Path

from .errors import ModsError
from .update_feed import (
    GITHUB_SOURCE,
    MAX_MANIFEST,
    MAX_PACKAGE,
    fetch,
    validate_package,
    validate_source,
    verified_manifest,
    version_tuple,
)

CHECK_INTERVAL = 6 * 60 * 60


class UpdateManager:
    """Private, persistent preferences; never overwrite settings, databases or active files."""

    def __init__(
        self, plugin_dir: Path, directory: Path, current_version: str, source: str | None = None
    ) -> None:
        version_tuple(current_version)
        if directory.is_symlink():
            raise ModsError("更新缓存目录不安全")
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        directory.chmod(0o700)
        self.directory = directory
        self.current_version = current_version
        self.signers = plugin_dir / "assets" / "update-allowed-signers"
        self._lock = threading.RLock()
        self._state: dict = {
            "source": validate_source(source) if source else None,
            "auto_check": True,
        }
        self._manifest: dict | None = None
        self._error: str | None = None
        state = directory / "preferences.json"
        try:
            if state.exists():
                if state.is_symlink() or state.stat().st_size > 16384:
                    raise ValueError
                parsed = json.loads(state.read_text())
                if not isinstance(parsed, dict) or type(parsed.get("auto_check", True)) is not bool:
                    raise ValueError
                self._state = {
                    **parsed,
                    "source": validate_source(parsed.get("source") or ""),
                    "auto_check": parsed.get("auto_check", True),
                }
        except (OSError, ValueError, ModsError):
            self._state = {"source": None, "auto_check": True}
            self._error = "更新设置无法读取，请重新保存更新来源"

    def _save(self) -> None:
        descriptor, name = tempfile.mkstemp(prefix=".preferences-", dir=self.directory)
        path = Path(name)
        try:
            with os.fdopen(descriptor, "w") as output:
                json.dump(self._state, output, separators=(",", ":"))
                output.flush()
                os.fsync(output.fileno())
            os.replace(path, self.directory / "preferences.json")
        finally:
            path.unlink(missing_ok=True)

    def status(self) -> dict:
        with self._lock:
            source = self._state["source"]
            latest = self._manifest["version"] if self._manifest else None
            return {
                "current_version": self.current_version,
                "latest_version": latest,
                "available": bool(
                    latest and version_tuple(latest) > version_tuple(self.current_version)
                ),
                "checked_at": self._state.get("checked_at"),
                "error": self._error,
                "source": source,
                "auto_check": self._state["auto_check"],
                "source_label": "GitHub 正式发布"
                if source == GITHUB_SOURCE
                else "局域网签名更新"
                if source
                else "尚未配置更新来源",
            }

    def configure(self, source: str, auto_check: bool) -> dict:
        normalized = validate_source(source)
        if type(auto_check) is not bool:
            raise ModsError("自动检查选项无效")
        with self._lock:
            changed = normalized != self._state["source"]
            self._state = {**self._state, "source": normalized, "auto_check": auto_check}
            if changed:
                self._manifest = None
                self._state.pop("checked_at", None)
                self._state.pop("prepared", None)
            self._error = None
            try:
                self._save()
            except OSError:
                raise ModsError("无法保存更新设置，请检查剩余空间后重试") from None
            return self.status()

    def check_due(self) -> bool:
        with self._lock:
            if not self._state["auto_check"] or not self._state["source"]:
                return False
            try:
                checked = datetime.fromisoformat(self._state.get("checked_at", ""))
                return (datetime.now(UTC) - checked).total_seconds() >= CHECK_INTERVAL
            except (ValueError, TypeError):
                return True

    def _fetch(self, url: str, maximum: int) -> bytes:
        return fetch(url, maximum, source=self._state["source"])

    def _check(self) -> None:
        source = self._state["source"]
        if not source:
            raise ModsError("请先配置更新来源，再检查或安装更新")
        raw = self._fetch(source + "/update.json", MAX_MANIFEST)
        signature = self._fetch(source + "/update.json.sig", MAX_MANIFEST)
        self._manifest = verified_manifest(raw, signature, self.signers)

    def check(self) -> dict:
        with self._lock:
            self._manifest = None
            self._error = None
            try:
                self._check()
            except ModsError as error:
                self._error = str(error)
            except (OSError, ValueError, TypeError):
                self._error = "检查更新失败，请检查网络和剩余空间后重试"
            self._state = {**self._state, "checked_at": datetime.now(UTC).isoformat()}
            try:
                self._save()
            except OSError:
                self._error = "更新检查完成，但无法保存状态，请检查剩余空间"
            return self.status()

    def prepare(self) -> dict:
        with self._lock:
            checked = self.check()
            if checked["error"]:
                raise ModsError(checked["error"])
            if not checked["available"] or self._manifest is None:
                raise ModsError("当前没有可安装的更新")
            manifest = self._manifest
            source = self._state["source"]
            filename = manifest["filename"] if source == GITHUB_SOURCE else "mods.zip"
            try:
                data = self._fetch(source + "/" + filename, MAX_PACKAGE)
                if (
                    len(data) != manifest["size"]
                    or hashlib.sha256(data).hexdigest() != manifest["sha256"]
                ):
                    raise ModsError("更新文件校验失败，已保留当前插件，请重新检查更新")
                validate_package(data, manifest, self.signers)
                destination = self.directory / manifest["filename"]
                descriptor, name = tempfile.mkstemp(prefix=".update-", dir=self.directory)
                temporary = Path(name)
                try:
                    with os.fdopen(descriptor, "wb") as output:
                        output.write(data)
                        output.flush()
                        os.fsync(output.fileno())
                    os.replace(temporary, destination)
                finally:
                    temporary.unlink(missing_ok=True)
                self._state = {
                    **self._state,
                    "prepared": {
                        "filename": manifest["filename"],
                        "sha256": manifest["sha256"],
                        "created_at": datetime.now(UTC).isoformat(),
                    },
                }
                self._save()
                return {
                    "artifact": destination.resolve().as_uri(),
                    "version": manifest["version"],
                    "sha256": manifest["sha256"],
                }
            except (OSError, ValueError, TypeError):
                raise ModsError("无法准备更新，请检查网络和剩余空间后重试") from None

    def installation_pending(self) -> bool:
        """Brief native-installer handoff window: preserve preferences during replacement."""
        with self._lock:
            marker = self._state.get("prepared")
            if not isinstance(marker, dict):
                return False
            try:
                age = (
                    datetime.now(UTC) - datetime.fromisoformat(marker["created_at"])
                ).total_seconds()
                filename = marker["filename"]
                if (
                    not 0 <= age < 300
                    or not isinstance(filename, str)
                    or Path(filename).name != filename
                ):
                    return False
                path = self.directory / filename
                if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_PACKAGE:
                    return False
                return hashlib.sha256(path.read_bytes()).hexdigest() == marker["sha256"]
            except (OSError, ValueError, TypeError, KeyError):
                return False
