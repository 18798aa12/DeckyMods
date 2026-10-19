"""Bounded Steam manifest enumeration and conservative runtime-tool exclusion."""

from __future__ import annotations

import os
import re
from pathlib import Path

MAX_LIBRARIES = 64
MAX_MANIFESTS = 4096
MAX_DIRECTORY_ENTRIES = 16384
_APP_ID = re.compile(r"[1-9][0-9]{0,9}\Z")
_MANIFEST = re.compile(r"appmanifest_([0-9]+)\.acf\Z")
_TOOL_IDS = frozenset(
    {
        "228980",  # Steamworks Common Redistributables
        "1070560",
        "1391110",
        "1628350",
        "4183110",  # Steam Linux Runtimes
        "1161040",
        "1493710",
        "3658110",
        "4628710",  # Proton runtimes
    }
)
_TOOL_NAME = re.compile(
    r"(?:steam linux runtime(?:\s+\d+(?:\.\d+)*(?:\s*\([a-z]+\))?)?"
    r"|steamworks common redistributables"
    r"|proton\s+(?:\d+(?:\.\d+)*(?:-\d+)?(?:\s*\([^)]{1,80}\))?"
    r"|experimental|hotfix|battleye runtime|easyanticheat runtime))\Z",
    re.IGNORECASE,
)


def valid_app_id(value: object) -> bool:
    """Steam AppIDs are canonical positive unsigned 32-bit integers."""
    return isinstance(value, str) and bool(_APP_ID.fullmatch(value)) and int(value) <= 0xFFFFFFFF


def is_runtime_tool(app_id: str, name: str) -> bool:
    """Exclude known runtimes without rejecting titles merely containing Proton."""
    return app_id in _TOOL_IDS or bool(_TOOL_NAME.fullmatch(" ".join(name.split())))


class InstallationRoots:
    """Prevent arbitrary manifests from creating independent state over one game tree."""

    def __init__(self) -> None:
        self.paths: frozenset[Path] = frozenset()
        self.ancestors: frozenset[Path] = frozenset()
        self.identities: frozenset[tuple[int, int]] = frozenset()

    def register(self, path: Path, *, exclusive: bool = False) -> bool:
        """Record reviewed roots first; reject overlapping dynamic roots and mount aliases."""
        info = path.stat()
        identity = (info.st_dev, info.st_ino)
        if exclusive and (
            identity in self.identities
            or path in self.paths
            or path in self.ancestors
            or any(parent in self.paths for parent in path.parents)
        ):
            return False
        self.paths = self.paths | {path}
        self.ancestors = self.ancestors | frozenset(path.parents)
        self.identities = self.identities | {identity}
        return True


def manifest_candidates(libraries: list[Path]) -> tuple[list[tuple[Path, str]], list[str]]:
    """Read only immediate manifest filenames, with global limits and no links."""
    result: list[tuple[Path, str]] = []
    issues: list[str] = []
    entries_seen = 0
    for library in libraries:
        directory = library / "steamapps"
        try:
            if directory.is_symlink():
                raise ValueError("symlinked Steam manifest directory")
            if not directory.is_dir():
                continue
            with os.scandir(directory) as entries:
                for entry in entries:
                    entries_seen += 1
                    if entries_seen > MAX_DIRECTORY_ENTRIES or len(result) >= MAX_MANIFESTS:
                        return result, [*issues, "Steam 游戏库清单数量过多，扫描已达到安全上限"]
                    match = _MANIFEST.fullmatch(entry.name)
                    if not match:
                        continue
                    app_id = match[1]
                    if not valid_app_id(app_id) or not entry.is_file(follow_symlinks=False):
                        issues.append("部分 Steam 安装清单无效，已跳过")
                        continue
                    result.append((library, app_id))
        except (OSError, ValueError):
            issues.append("部分 Steam 安装清单无法安全读取，请检查 Steam 存储设置")
    return result, issues


def discovered_entry(app_id: str, name: str) -> dict:
    """Unknown titles support explicit author-specified root ZIPs, with no guessed adapter."""
    return {
        "id": f"steam-{app_id}",
        "name": name,
        "series": "steam-installed",
        "series_name": "其他已安装游戏",
        "steam_app_ids": [app_id],
        "nexus_domain": "",
        "adapter": "catalog",
        "adapter_config": {},
        "support": "catalog",
        "requirements": [
            "已从 Steam 安装清单识别；尚无专用适配与已核实的 Nexus 游戏映射。",
            "请按 MOD 作者说明准备与游戏根目录结构一致的本地 ZIP 压缩包，并明确选择根目录安装。",
            "前置加载器、启动项和版本兼容性须按作者说明配置；仅列出游戏不代表已验证 MOD 兼容性。",
        ],
        "sources": [f"https://store.steampowered.com/app/{app_id}/"],
        "validation": "Steam 本地安装清单验证；未进行 MOD 硬件兼容性测试。",
    }
