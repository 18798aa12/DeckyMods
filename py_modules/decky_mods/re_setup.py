"""Resident Evil runtime evidence and separately backed-up REFramework preferences."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from .deployment import Deployment
from .errors import ModsError
from .paths import private_directory

CONFIG_NAME = "re2_fw_config.txt"
LOOSE_KEY = "LooseFileLoader_Enabled"
PAK_KEY = "IntegrityCheckBypass_LoadPakDirectory"
MODERN = {
    "residentevil22019",
    "residentevil32020",
    "residentevil42023",
    "residentevil7",
    "residentevilvillage",
    "residentevilrequiem",
}
_LEGACY_TDB = {"residentevil22019": 66, "residentevil32020": 67, "residentevil7": 49}


def _read_file(path: Path, maximum: int = 512 * 1024) -> bytes | None:
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
                raise ModsError("前置配置不是普通文件或过大，请手动核对")
            return stream.read(maximum + 1)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise ModsError("无法安全读取前置配置，请检查链接和权限") from error


def config_document(root: Path) -> tuple[bytes, str, dict[str, bool]]:
    payload = _read_file(root / CONFIG_NAME)
    if payload is None:
        raise ModsError("请先安装匹配的 REFramework 并运行一次游戏，生成前置配置")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeError as error:
        raise ModsError("REFramework 配置编码无效，请手动检查") from error
    if "\x00" in text:
        raise ModsError("REFramework 配置包含空字符")
    flags: dict[str, bool] = {}
    for line in text.splitlines():
        if line.strip() and not line.lstrip().startswith(("#", ";")) and "=" not in line:
            raise ModsError("REFramework 配置格式无效，请手动检查")
        key, separator, value = line.partition("=")
        key = key.strip()
        if separator and key in {LOOSE_KEY, PAK_KEY}:
            if key in flags or value.strip().lower() not in {"true", "false"}:
                raise ModsError("REFramework 配置存在重复或无效的资源加载选项")
            flags[key] = value.strip().lower() == "true"
    return payload, text, flags


def _runtime(root: Path) -> dict:
    result = {
        "runtime_tdb": None,
        "renderer": None,
        "runtime_evidence": False,
        "script_count": 0,
        "last_run_at": None,
    }
    path = root / "re2_framework_log.txt"
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                return result
            head = stream.read(256 * 1024)
            if info.st_size > len(head):
                stream.seek(max(len(head), info.st_size - 256 * 1024))
            text = (head + stream.read(256 * 1024)).decode("utf-8", errors="replace")
        tdb = re.findall(r"TDB Version\s*:\s*(\d{1,4})", text)
        renderer = re.findall(r"BackBufferRenderer\s+(D3D1[12])\s+initialized", text)
        scripts = set(re.findall(r"Running script[^\r\n]*?([\w.-]+\.lua)", text))
        result = {
            "runtime_tdb": int(tdb[-1]) if tdb else None,
            "renderer": renderer[-1] if renderer else None,
            "runtime_evidence": bool(tdb and renderer),
            "script_count": len(scripts),
            "last_run_at": datetime.fromtimestamp(info.st_mtime, UTC).isoformat(),
        }
    except FileNotFoundError:
        pass
    except OSError as error:
        raise ModsError("上次运行日志无法安全读取，请检查权限") from error
    return result


def inspect_resident(game: dict) -> dict:
    supported = game.get("series") == "resident-evil" and game.get("installed") is True
    modern = game.get("id") in MODERN
    root = Path(game.get("path") or "/")
    config_exists, config_valid, flags = False, False, {}
    warnings = []
    if supported and modern:
        try:
            config_exists = (root / CONFIG_NAME).exists()
            _, _, flags = config_document(root)
            config_valid = True
        except ModsError as error:
            warnings.append(str(error))
    runtime = (
        _runtime(root)
        if supported and modern
        else {
            "runtime_tdb": None,
            "renderer": None,
            "runtime_evidence": False,
            "script_count": 0,
            "last_run_at": None,
        }
    )
    if runtime["runtime_tdb"] == _LEGACY_TDB.get(game.get("id")) and runtime["runtime_tdb"]:
        warnings.append(
            "上次日志为旧非 RT 分支，需要该分支的旧版 REFramework，不能使用当前通用版。"
        )
    if supported:
        warnings.append("日志只证明上次运行情况；游戏或 MOD 更新后仍须核对作者的版本与前置要求。")
    try:
        loader = modern and stat.S_ISREG((root / "dinput8.dll").lstat().st_mode)
    except OSError:
        loader = False
    return {
        "supported": bool(supported),
        "family": "RE Engine / REFramework" if modern else "旧引擎资源替换",
        "build_id": game.get("build_id"),
        **runtime,
        "loader_present": bool(loader),
        "config_exists": config_exists,
        "config_valid": config_valid,
        "loose_enabled": flags.get(LOOSE_KEY, False),
        "pak_directory_enabled": flags.get(PAK_KEY, False),
        "config_backup_available": False,
        "warnings": warnings,
    }


class RESettings:
    """Keep loader preferences separate from resources, using the deployment journal."""

    def __init__(self, directory: Path) -> None:
        private_directory(directory)
        self.directory = directory
        self.engine = Deployment(directory / "configuration")

    def status(self, game: dict) -> dict:
        return {
            **inspect_resident(game),
            "config_backup_available": bool(
                self.engine.list_mods(game["id"]) or self.engine.db.pending(game["id"])
            ),
        }

    def apply(self, game: dict, requirements: list[str]) -> dict:
        if (
            game.get("id") not in MODERN
            or not isinstance(requirements, list)
            or not requirements
            or any(key not in {LOOSE_KEY, PAK_KEY} for key in requirements)
            or (PAK_KEY in requirements and game["id"] != "residentevilrequiem")
        ):
            raise ModsError("此游戏的前置配置要求尚未适配")
        self.engine._check(game)
        self.engine.recover(game)
        payload, text, flags = config_document(Path(game["path"]))
        if not self.status(game)["loader_present"]:
            raise ModsError("请先安装匹配的官方 REFramework 加载器")
        if all(flags.get(key) for key in requirements):
            return self.status(game)
        newline = "\r\n" if "\r\n" in text else "\n"
        lines = []
        seen = set()
        for line in text.splitlines(keepends=True):
            key, separator, _ = line.partition("=")
            if separator and key.strip() in requirements:
                seen.add(key.strip())
                ending = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
                lines.append(key + "=true" + ending)
            else:
                lines.append(line)
        updated = "".join(lines)
        for key in requirements:
            if key not in seen:
                if updated and not updated.endswith(("\n", "\r")):
                    updated += newline
                updated += key + "=true" + newline
        encoded = (
            b"\xef\xbb\xbf" if payload.startswith(b"\xef\xbb\xbf") else b""
        ) + updated.encode("utf-8")
        with self.engine.lock, tempfile.TemporaryDirectory(dir=self.directory) as staging:
            # Compare with the immutable bytes inspected, before prepare captures a baseline.
            if _read_file(Path(game["path"]) / CONFIG_NAME) != payload:
                raise ModsError("前置配置被外部修改，请重新检查")
            source = Path(staging) / CONFIG_NAME
            source.write_bytes(encoded)
            mapping = {
                "files": [{"source": CONFIG_NAME, "target": CONFIG_NAME}],
                "expected_targets": {CONFIG_NAME: hashlib.sha256(payload).hexdigest()},
                "warnings": [],
                "requirements": [],
                "blocked_reason": None,
            }
            plan = self.engine.prepare(game, "REFramework 资源加载设置", Path(staging), mapping)
            self.engine.install(game, plan["id"], allow_conflicts=True)
        return self.status(game)

    def restore(self, game: dict) -> dict:
        self.engine._check(game)
        self.engine.recover(game)
        for mod in reversed(self.engine.list_mods(game["id"])):
            self.engine.uninstall(game, mod["id"])
        return self.status(game)
