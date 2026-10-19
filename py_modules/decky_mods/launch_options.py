"""Private launch-option intent journals; Steam writes remain in the native UI bridge."""

from __future__ import annotations

import json
import os
import re
import stat
import uuid
from pathlib import Path

from .errors import ModsError
from .launch_parser import merge_options, validate_text
from .paths import atomic_write, private_directory

_CORRUPT = "启动项备份或记录无效，请保留备份并联系维护者；没有修改 Steam 设置。"
_DIVERGED = "启动选项已在外部更改，已停止自动恢复或覆盖，请先在 Steam 属性中检查。"


class LaunchOptions:
    """Recognize only registry-reviewed REFramework installations and journal edits."""

    def __init__(self, directory: Path) -> None:
        if not directory.is_absolute() or any(path.is_symlink() for path in directory.parents):
            raise ModsError("启动项私有目录不能经过符号链接，请检查插件数据目录。")
        self.directory = directory
        private_directory(directory)

    @staticmethod
    def _identity(game: dict) -> str | None:
        app_id = game.get("app_id")
        if (
            game.get("adapter") != "reframework"
            or not game.get("installed")
            or not isinstance(app_id, str)
            or not re.fullmatch(r"[1-9][0-9]{0,9}", app_id)
            or int(app_id) > 4294967295
            or not isinstance(game.get("id"), str)
            or not game["id"]
            or not isinstance(game.get("path"), str)
        ):
            return None
        root = Path(game["path"])
        try:
            if (
                not root.is_absolute()
                or root.is_symlink()
                or not root.is_dir()
                or any(path.is_symlink() for path in root.parents)
            ):
                return None
        except OSError:
            return None
        return app_id

    @staticmethod
    def _loader(game: dict) -> bool:
        try:
            return stat.S_ISREG((Path(game["path"]) / "dinput8.dll").lstat().st_mode)
        except OSError:
            return False

    @staticmethod
    def _initial(game: dict, app_id: str) -> dict:
        return {
            "version": 1,
            "game_id": game["id"],
            "app_id": app_id,
            "auto_enabled": True,
            "original": None,
            "last_written": None,
            "pending": None,
            "restore_safe": True,
        }

    def _read(self, game: dict, app_id: str) -> dict:
        path = self.directory / f"{app_id}.json"
        try:
            descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except FileNotFoundError:
            return self._initial(game, app_id)
        except OSError:
            raise ModsError(_CORRUPT) from None
        try:
            with os.fdopen(descriptor, "rb") as stream:
                info = os.fstat(stream.fileno())
                if (
                    not stat.S_ISREG(info.st_mode)
                    or info.st_uid != os.geteuid()
                    or info.st_nlink != 1
                    or stat.S_IMODE(info.st_mode) != 0o600
                    or info.st_size > 262144
                ):
                    raise ModsError(_CORRUPT)
                result = json.loads(stream.read(262145))
            self._validate_state(result, game, app_id)
            return result
        except (OSError, UnicodeError, ValueError, TypeError, KeyError):
            raise ModsError(_CORRUPT) from None

    @staticmethod
    def _validate_state(state: dict, game: dict, app_id: str) -> None:
        if (
            not isinstance(state, dict)
            or state.get("version") != 1
            or state.get("game_id") != game["id"]
            or state.get("app_id") != app_id
            or not isinstance(state.get("auto_enabled"), bool)
            or not isinstance(state.get("restore_safe"), bool)
            or "pending" not in state
        ):
            raise ModsError(_CORRUPT)
        for key in ("original", "last_written"):
            if key not in state:
                raise ModsError(_CORRUPT)
            if state[key] is not None:
                validate_text(state[key])
        pending = state.get("pending")
        if state["original"] is None and (state["last_written"] is not None or pending is not None):
            raise ModsError(_CORRUPT)
        if pending is not None:
            if (
                not isinstance(pending, dict)
                or not isinstance(pending.get("id"), str)
                or not re.fullmatch(r"[a-f0-9]{32}", pending["id"])
                or not isinstance(pending.get("restore"), bool)
            ):
                raise ModsError(_CORRUPT)
            validate_text(pending.get("before"))
            validate_text(pending.get("after"))

    def _write(self, app_id: str, state: dict) -> None:
        try:
            atomic_write(
                self.directory / f"{app_id}.json",
                json.dumps(state, ensure_ascii=False).encode("utf-8"),
            )
        except (OSError, ValueError, UnicodeError):
            raise ModsError("无法安全保存启动项备份，请检查插件数据目录权限和剩余空间。") from None

    def status(self, game: dict) -> dict:
        """Report safe requirements without exposing private launch-option strings."""
        app_id = self._identity(game)
        if app_id is None:
            return {
                "supported": False,
                "required": False,
                "reason": "当前仅识别已安装且适配完成的 REFramework 游戏。",
                "app_id": None,
                "auto_enabled": True,
                "backup_available": False,
            }
        state = self._read(game, app_id)
        required = self._loader(game)
        return {
            "supported": True,
            "required": required,
            "reason": (
                "检测到后续外部启动项修改；可继续合并，为保留修改已禁止恢复旧备份。"
                if not state["restore_safe"]
                else (
                    "检测到 REFramework，需要 Proton DLL 启动项；将保留已有插帧与其他参数。"
                    if required
                    else "尚未检测到游戏根目录中的 REFramework dinput8.dll，不会自动添加启动项。"
                )
            ),
            "app_id": app_id,
            "auto_enabled": state["auto_enabled"],
            "backup_available": state["original"] is not None,
        }

    def _guard(self, game: dict, require_loader: bool = True) -> str:
        app_id = self._identity(game)
        if app_id is None:
            raise ModsError("未找到支持自动配置的已安装游戏，请刷新游戏列表。")
        if game.get("running") or game.get("updating"):
            raise ModsError("请先完全退出游戏并等待 Steam 更新完成，再配置启动选项。")
        if require_loader and not self._loader(game):
            raise ModsError("未检测到有效 REFramework 加载器，请先安装匹配的官方版本。")
        return app_id

    def set_auto(self, game: dict, enabled: bool) -> dict:
        """Store a preference; this never writes Steam's launch options."""
        if not isinstance(enabled, bool):
            raise ModsError("自动配置选项必须为开启或关闭。")
        app_id = self._guard(game, require_loader=False)
        state = self._read(game, app_id)
        self._write(app_id, {**state, "auto_enabled": enabled})
        return self.status(game)

    def _complete(self, app_id: str, state: dict) -> dict:
        pending = state["pending"]
        updated = {
            **state,
            "last_written": pending["after"],
            "pending": None,
            "auto_enabled": False if pending["restore"] else state["auto_enabled"],
        }
        self._write(app_id, updated)
        return updated

    def _observe(self, app_id: str, state: dict, current: str) -> dict:
        """Once external edits are seen, an old full snapshot is never safe to restore."""
        expected = state["last_written"] if state["last_written"] is not None else state["original"]
        observed = current
        pending = state["pending"]
        if pending is not None and current in (pending["before"], pending["after"]):
            # An interrupted Steam write legitimately changes before to after. Compare
            # its baseline to the preceding write, including backup-only interruptions.
            observed = pending["before"]
        if state["restore_safe"] and expected is not None and observed != expected:
            updated = {**state, "restore_safe": False}
            self._write(app_id, updated)
            return updated
        return state

    @staticmethod
    def _change(app_id: str, pending: dict) -> dict:
        return {
            "id": pending["id"],
            "app_id": app_id,
            "before": pending["before"],
            "after": pending["after"],
            "changed": pending["before"] != pending["after"],
        }

    def prepare(self, game: dict, current: str, restore: bool = False) -> dict:
        """Persist intent before a native Steam mutation; retry safely after interruption."""
        if not isinstance(restore, bool):
            raise ModsError("恢复选项无效。")
        app_id = self._guard(game, require_loader=not restore)
        validate_text(current)
        state = self._observe(app_id, self._read(game, app_id), current)
        if restore and not state["restore_safe"]:
            raise ModsError(_DIVERGED)
        if not restore and not state["auto_enabled"]:
            raise ModsError("自动配置已关闭，请先开启自动配置启动项。")
        pending = state["pending"]
        if pending is not None:
            if current == pending["after"]:
                state = self._complete(app_id, state)
            elif current == pending["before"]:
                if pending["restore"] != restore:
                    raise ModsError("上次启动项操作尚未完成，请先重试上次操作。")
                return self._change(app_id, pending)
            else:
                raise ModsError(_DIVERGED)
        if restore:
            if state["original"] is None or state["last_written"] is None:
                raise ModsError("没有可恢复的插件启动项备份。")
            if current != state["last_written"]:
                raise ModsError(_DIVERGED)
            after = state["original"]
        else:
            if not state["auto_enabled"]:
                raise ModsError("自动配置已关闭，请先开启自动配置启动项。")
            after = merge_options(current)
        if after == current:
            if restore:
                self._write(app_id, {**state, "auto_enabled": False})
            return {"id": "", "app_id": app_id, "before": current, "after": after, "changed": False}
        if state["original"] is None:
            state = {**state, "original": current}
            self._write(app_id, state)
        pending = {"id": uuid.uuid4().hex, "before": current, "after": after, "restore": restore}
        self._write(app_id, {**state, "pending": pending})
        return self._change(app_id, pending)

    def finish(self, game: dict, change_id: str, observed: str) -> dict:
        """Confirm only the exact prepared command returned by a fresh Steam read."""
        app_id = self._guard(game, require_loader=False)
        validate_text(observed)
        state = self._read(game, app_id)
        pending = state["pending"]
        if pending is None or pending["id"] != change_id:
            raise ModsError("启动项操作标识已失效，请重新检查。")
        state = self._observe(app_id, state, observed)
        if pending["after"] != observed:
            raise ModsError("Steam 尚未保存预期的启动选项，请重试；原始备份已保留。")
        self._complete(app_id, state)
        return self.status(game)
