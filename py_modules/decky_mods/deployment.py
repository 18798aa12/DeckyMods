"""Journaled deployment and immutable MOD layers with checksum-aware recovery."""

import os
import shutil
import threading
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from .database import Database
from .errors import ModsError
from .gamefs import GameFiles, fingerprint
from .layers import effective_files
from .objects import Objects
from .paths import private_directory, relative_path


class Deployment:
    def __init__(self, directory: Path, *, fault: Callable[[int, str], None] | None = None):
        private_directory(directory)
        self.objects = Objects(directory / "objects")
        self.db = Database(directory)
        self.lock = threading.RLock()
        self.fault = fault

    def _state(self, game: dict) -> dict:
        actual = fingerprint(game)
        state = self.db.game(game["id"])
        if state is not None:
            if any(state["fingerprint"][key] != actual[key] for key in ("path", "device", "inode")):
                if state["mods"]:
                    raise ModsError("游戏版本或目录发生变化，请先恢复旧安装记录再重新导入")
                state = None
            elif state is not None:
                state = {**state, "fingerprint": actual}
        return state or {
            "fingerprint": actual,
            "mods": [],
            "baseline": {},
            "modes": {},
            "managed": {},
            "deployed": {},
        }

    def _check(self, game: dict) -> None:
        if game.get("updating"):
            raise ModsError("Steam 正在更新或验证游戏，请等待完成后再修改 MOD")
        if game.get("running"):
            raise ModsError("游戏正在运行，请先退出游戏再修改 MOD")

    def prepare(
        self, game: dict, name: str, extracted: Path, mapping: dict, identity: dict | None = None
    ) -> dict:
        with self.lock:
            self._check(game)
            self.recover(game)
            state = self._state(game)
            if not isinstance(name, str) or not name.strip() or len(name) > 120:
                raise ModsError("MOD 名称须为 1～120 个字符")
            files = []
            seen: set[str] = set()
            for entry in mapping["files"]:
                source, target = relative_path(entry["source"]), relative_path(entry["target"])
                path = extracted / source
                if (
                    path.is_symlink()
                    or not path.is_file()
                    or not path.resolve().is_relative_to(extracted.resolve())
                ):
                    raise ModsError("解包文件不在私有 staging 内")
                if target.casefold() in seen:
                    raise ModsError("MOD 内含重复目标文件")
                seen.add(target.casefold())
                descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(descriptor, "rb") as stream:
                    digest, size = self.objects.put(stream)
                files.append(
                    {
                        "target": target,
                        "hash": digest,
                        "size": size,
                        "kind": entry.get("kind", "file"),
                    }
                )
            mod = {
                "id": uuid.uuid4().hex,
                "name": name.strip(),
                "enabled": True,
                "installed_at": datetime.now(UTC).isoformat(),
                "files": files,
                "nexus_mod_id": (identity or {}).get("mod_id"),
                "nexus_file_id": (identity or {}).get("file_id"),
                "source_url": (identity or {}).get("source_url"),
                "details": (identity or {}).get("details"),
            }
            previous_names = {
                file["target"].casefold(): file["target"]
                for existing in state["mods"]
                for file in existing["files"]
            }
            if any(
                file["target"].casefold() in previous_names
                and previous_names[file["target"].casefold()] != file["target"]
                for file in files
            ):
                raise ModsError("MOD 与已管理文件存在大小写冲突，请统一文件名后重试")
            game_files = GameFiles(game, self.objects, expected=state["fingerprint"])
            desired = effective_files(game, state, [*state["mods"], mod])
            conflicts = sorted(
                target
                for target, digest in desired.items()
                if game_files.hash(target) is not None
                and game_files.hash(target) != digest
                and state["managed"].get(target) != digest
            )
            blocked = mapping.get("blocked_reason") or (None if files else "没有已适配的 MOD 文件")
            plan = {
                "id": uuid.uuid4().hex,
                "game_id": game["id"],
                "name": name.strip(),
                "files_count": len(files),
                "targets": [file["target"] for file in files],
                "bytes": sum(file["size"] for file in files),
                "conflicts": conflicts,
                "warnings": mapping.get("warnings", []),
                "requirements": mapping.get("requirements", []),
                "config_requirements": mapping.get("config_requirements", []),
                "expected_targets": mapping.get("expected_targets", {}),
                "blocked_reason": blocked,
                "can_install": blocked is None,
                "fingerprint": fingerprint(game),
                "mod": mod,
            }
            self.db.save_plan(plan)
            return self._public_plan(plan)

    @staticmethod
    def _public_plan(plan: dict) -> dict:
        return {
            key: value
            for key, value in plan.items()
            if key not in ("fingerprint", "mod", "expected_targets")
        }

    def get_plan(self, plan_id: str) -> dict:
        return self._public_plan(self.db.plan(plan_id))

    @staticmethod
    def _public_mod(mod: dict) -> dict:
        return {
            **{key: value for key, value in mod.items() if key not in {"files", "details"}},
            "files_count": len(mod["files"]),
        }

    def list_mods(self, game_id: str) -> list[dict]:
        state = self.db.game(game_id)
        return [self._public_mod(mod) for mod in (state or {}).get("mods", [])]

    def install(self, game: dict, plan_id: str, allow_conflicts: bool = False) -> dict:
        if type(allow_conflicts) is not bool:
            raise ModsError("覆盖确认必须为布尔值")
        with self.lock:
            self._check(game)
            self.recover(game)
            plan = self.db.plan(plan_id)
            if plan["game_id"] != game["id"] or plan["fingerprint"] != fingerprint(game):
                raise ModsError("游戏或版本变化，请重新生成安装预览")
            if not plan["can_install"]:
                raise ModsError(plan["blocked_reason"])
            if plan["conflicts"] and not allow_conflicts:
                raise ModsError("目标存在覆盖冲突，请在预览中确认")
            state = self._state(game)
            mod = plan["mod"]
            self._apply(
                game,
                state,
                [*state["mods"], mod],
                plan_id=plan_id,
                allow_conflicts=allow_conflicts,
                expected_targets=plan.get("expected_targets", {}),
            )
            return self._public_mod(mod)

    def set_enabled(self, game: dict, mod_id: str, enabled: bool) -> None:
        if type(enabled) is not bool:
            raise ModsError("启用状态必须为布尔值")
        with self.lock:
            self._check(game)
            self.recover(game)
            state = self._state(game)
            if not any(mod["id"] == mod_id for mod in state["mods"]):
                raise ModsError("MOD 记录不存在，请刷新")
            mods = [
                {**mod, "enabled": enabled} if mod["id"] == mod_id else mod for mod in state["mods"]
            ]
            self._apply(game, state, mods, allow_conflicts=True)

    def uninstall(self, game: dict, mod_id: str) -> None:
        with self.lock:
            self._check(game)
            self.recover(game)
            state = self._state(game)
            if not any(mod["id"] == mod_id for mod in state["mods"]):
                raise ModsError("MOD 记录不存在，请刷新")
            self._apply(
                game,
                state,
                [mod for mod in state["mods"] if mod["id"] != mod_id],
                allow_conflicts=True,
            )

    def _apply(
        self,
        game: dict,
        state: dict,
        mods: list[dict],
        *,
        plan_id: str | None = None,
        allow_conflicts: bool = False,
        expected_targets: dict[str, str | None] | None = None,
    ) -> None:
        game_files = GameFiles(game, self.objects, expected=state["fingerprint"])
        for target, expected in (expected_targets or {}).items():
            if game_files.hash(target) != expected:
                raise ModsError("准备修改的配置被外部修改，已保留新内容")
        for target, expected in state["deployed"].items():
            if game_files.hash(target) != expected:
                raise ModsError("游戏文件已被外部修改，存在冲突；未覆盖或删除新文件")
        desired = effective_files(game, state, mods)
        baseline, modes = dict(state["baseline"]), dict(state["modes"])
        for target in desired:
            if target not in baseline:
                digest, mode = game_files.capture(target)
                if (
                    expected_targets
                    and target in expected_targets
                    and digest != expected_targets[target]
                ):
                    raise ModsError("配置在备份时被外部修改，已保留新内容")
                if digest is not None and digest != desired[target] and not allow_conflicts:
                    raise ModsError("目标文件发生覆盖冲突，请重新预览并确认")
                baseline[target], modes[target] = digest, mode
        all_targets = set(baseline) | set(state["deployed"]) | set(desired)
        operation_id = uuid.uuid4().hex
        steps = []
        for index, target in enumerate(sorted(all_targets)):
            # Pin to the bytes actually validated/backed up. Re-reading a new
            # value here must never silently adopt a concurrent Steam update.
            before = state["deployed"].get(target, baseline.get(target))
            if game_files.hash(target) != before:
                raise ModsError("游戏文件在备份后被外部修改，已保留现状；请重新预览")
            after = desired.get(target, baseline.get(target))
            if before != after:
                if after:
                    self.objects.verify(after)
                steps.append(
                    {
                        "target": target,
                        "before": before,
                        "after": after,
                        "mode": modes.get(target, 0o644),
                        "temp": f".deckymods-{operation_id}{index:x}",
                    }
                )
        required = sum(
            self.objects.path(step["after"]).stat().st_size for step in steps if step["after"]
        )
        if shutil.disk_usage(game["path"]).free < required + 8 * 1024**2:
            raise ModsError("游戏所在磁盘空间不足，未开始部署")
        retained = {
            file["target"] for mod in mods for file in mod["files"] if file["kind"] != "re_pak"
        } | set(desired)
        next_state = {
            "fingerprint": state["fingerprint"],
            "mods": mods,
            "baseline": {key: value for key, value in baseline.items() if key in retained},
            "modes": {key: value for key, value in modes.items() if key in retained},
            "managed": desired,
            "deployed": {key: desired.get(key, baseline.get(key)) for key in retained},
        }
        operation = {
            "id": operation_id,
            "game_id": game["id"],
            "fingerprint": state["fingerprint"],
            "plan_id": plan_id,
            "steps": steps,
        }
        self.db.begin(operation)
        try:
            for index, step in enumerate(steps):
                game_files.apply(
                    step["target"], step["before"], step["after"], step["mode"], step["temp"]
                )
                if self.fault:
                    self.fault(index, step["target"])
            self.db.finish(operation, next_state, committed=True)
        except Exception as error:
            try:
                self._rollback(game, operation)
            except Exception as recovery:
                self.db.failed_recovery(operation)
                raise ModsError(
                    "操作未完成，自动恢复遇到外部修改；已保留备份，请先恢复"
                ) from recovery
            raise ModsError("部署失败，已恢复操作前文件；请检查磁盘和权限") from error

    def _rollback(self, game: dict, operation: dict) -> None:
        game_files = GameFiles(game, self.objects, expected=operation["fingerprint"])
        # Validate the ENTIRE interrupted operation before restoring any file.
        # A displaced unknown file can be a concurrent Steam/user update. A
        # partial new temp is safe to quarantine only while its target is still
        # exactly the pre-operation file.
        quarantine = []
        for step in operation["steps"]:
            actual = game_files.hash(step["target"])
            if actual not in (step["before"], step["after"]):
                raise ModsError("恢复目标被外部修改，已保留现状和备份")
            for temporary in (step["temp"], step["temp"] + "_r"):
                digest = game_files.temp_hash(step["target"], temporary)
                if digest is not None and digest not in (step["before"], step["after"]):
                    # Rollback writes in the opposite direction: its incomplete
                    # staging file is safe only while the deployed file remains.
                    unchanged = step["after"] if temporary.endswith("_r") else step["before"]
                    if actual != unchanged:
                        raise ModsError("中断操作留下外部修改的原文件，恢复前需解决冲突")
                    quarantine.append((step, temporary, digest))
        for step, temporary, digest in quarantine:
            retained = game_files.retain_temp(step["target"], temporary)
            if retained != digest:
                raise ModsError("恢复临时文件读取中发生变化，已保留")
            operation = {
                **operation,
                "quarantined": [
                    *operation.get("quarantined", []),
                    {"target": step["target"], "hash": retained, "reason": "partial temporary"},
                ],
            }
            self.db.rewrite(operation)
            game_files.clean_temp(step["target"], temporary, {retained})
        for step in reversed(operation["steps"]):
            actual = game_files.hash(step["target"])
            if actual not in (step["before"], step["after"]):
                raise ModsError("恢复目标被外部修改，已保留现状和备份")
            if actual != step["before"]:
                game_files.clean_temp(
                    step["target"], step["temp"] + "_r", {step["before"], step["after"]}
                )
                game_files.apply(
                    step["target"], actual, step["before"], step["mode"], step["temp"] + "_r"
                )
            for name in (step["temp"], step["temp"] + "_r"):
                try:
                    game_files.clean_temp(step["target"], name, {step["before"], step["after"]})
                except FileNotFoundError:
                    pass
        self.db.finish(operation, {}, committed=False)

    def recover(self, game: dict) -> None:
        with self.lock:
            self._check(game)
            for operation in self.db.pending(game["id"]):
                if operation["fingerprint"] != fingerprint(game):
                    raise ModsError("未完成操作需要原游戏目录和版本，请插回原存储设备再恢复")
                try:
                    self._rollback(game, operation)
                except Exception as error:
                    self.db.failed_recovery(operation)
                    raise ModsError("恢复被外部修改阻止，已保留文件和备份") from error
