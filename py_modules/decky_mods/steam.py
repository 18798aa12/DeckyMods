"""Discover installed Steam libraries without trusting archive or UI filesystem paths."""

from __future__ import annotations

import copy
import os
import re
import sys
from pathlib import Path

from .errors import ModsError
from .steam_library import (
    MAX_LIBRARIES,
    InstallationRoots,
    discovered_entry,
    is_runtime_tool,
    manifest_candidates,
    valid_app_id,
)
from .vdf import read_vdf

_APP_ID = re.compile(r"[1-9][0-9]{0,9}\Z")
_PROC_ROOT = Path("/proc")


def _inside(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _process_matches(process: Path, candidates: dict[str, Path]) -> set[str]:
    """An opaque browser/keyring process must not block unrelated game libraries."""
    evidence: list[str] = []
    for name in ("exe", "cwd"):
        try:
            evidence.append(os.readlink(process / name).replace("\\", "/").casefold())
        except OSError:
            continue
    try:
        with (process / "cmdline").open("rb") as stream:
            evidence.extend(
                stream.read(131072)
                .decode("utf-8", errors="replace")
                .replace("\\", "/")
                .casefold()
                .split("\0")
            )
    except OSError:
        pass
    matched: set[str] = set()
    for app_id, root in candidates.items():
        prefix = root.as_posix().casefold()
        if any(value == prefix or prefix + "/" in value for value in evidence):
            matched.add(app_id)
    return matched


def _running_apps(
    candidates: dict[str, Path], *, match_paths: bool = False
) -> tuple[set[str], set[str]]:
    """Read our own processes, retaining uncertainty only for plausible game processes."""
    if sys.platform != "linux":
        return set(), set()
    running: set[str] = set()
    uncertain: set[str] = set()
    try:
        processes = tuple(_PROC_ROOT.iterdir())
    except OSError:
        return set(), set(candidates)
    for process in processes:
        if not process.name.isdecimal():
            continue
        try:
            if process.stat().st_uid != os.getuid():
                continue
            if match_paths:
                running.update(_process_matches(process, candidates))
            with (process / "environ").open("rb") as stream:
                values = stream.read(131072).split(b"\0")
            for field in values:
                key, sep, value = field.partition(b"=")
                if sep and key in {b"SteamAppId", b"SteamGameId"}:
                    ident = value.decode("ascii", errors="ignore")
                    if _APP_ID.fullmatch(ident):
                        running.add(ident)
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError:
            uncertain.update(_process_matches(process, candidates))
        except OSError:
            uncertain.update(_process_matches(process, candidates))
    return running, uncertain


class SteamDiscovery:
    """Resolve reviewed adapters and other installed games from validated Steam manifests."""

    def __init__(self, catalog: list[dict], home: Path | None = None) -> None:
        self.catalog = copy.deepcopy(catalog)
        self.home = (home or Path.home()).resolve()
        self.issues: tuple[str, ...] = ()

    def _libraries(self) -> tuple[list[Path], list[str]]:
        anchors = (
            self.home / ".local/share/Steam",
            self.home / ".steam/steam",
            self.home / ".steam/root",
            self.home / ".steam/debian-installation",
        )
        libraries: set[Path] = set()
        issues: list[str] = []
        for anchor in anchors:
            try:
                if not anchor.is_dir():
                    continue
                steam = anchor.resolve(strict=True)
                if steam not in libraries and len(libraries) >= MAX_LIBRARIES:
                    raise ValueError("too many Steam libraries")
                libraries.add(steam)
                for config in (
                    steam / "steamapps/libraryfolders.vdf",
                    steam / "config/libraryfolders.vdf",
                ):
                    if not config.exists():
                        continue
                    values = read_vdf(config).get("libraryfolders", {})
                    if not isinstance(values, dict):
                        raise ValueError("invalid library list")
                    for key, item in values.items():
                        if not key.isdecimal():
                            continue
                        raw = item.get("path") if isinstance(item, dict) else item
                        if not isinstance(raw, str) or not raw or "\x00" in raw:
                            continue
                        candidate = Path(raw)
                        if candidate.is_absolute() and candidate.is_dir():
                            resolved = candidate.resolve(strict=True)
                            if resolved not in libraries and len(libraries) >= MAX_LIBRARIES:
                                raise ValueError("too many Steam libraries")
                            libraries.add(resolved)
            except (OSError, UnicodeError, ValueError):
                issues.append("部分 Steam 游戏库清单无法读取，请检查 Steam 存储设置")
        return sorted(libraries, key=str), issues

    @staticmethod
    def _installed(library: Path, app_id: str) -> dict | None:
        if not valid_app_id(app_id):
            raise ValueError("invalid Steam AppID")
        if (library / "steamapps").is_symlink():
            raise ValueError("symlinked Steam manifest directory")
        manifest = library / "steamapps" / f"appmanifest_{app_id}.acf"
        if not manifest.exists():
            return None
        state = read_vdf(manifest).get("AppState")
        if not isinstance(state, dict) or state.get("appid") != app_id:
            raise ValueError("mismatched Steam manifest")
        name = state.get("installdir", "")
        if (
            not isinstance(name, str)
            or not name
            or name in {".", ".."}
            or any(char in name for char in "/\\\x00")
            or Path(name).is_absolute()
        ):
            raise ValueError("unsafe Steam install directory")
        raw_common = library / "steamapps/common"
        if raw_common.is_symlink() or (raw_common / name).is_symlink():
            raise ValueError("symlinked Steam game directory")
        common = raw_common.resolve(strict=True)
        # A declared library may itself be a mount/symlink, its internal roots may not escape it.
        if not _inside(common, library):
            raise ValueError("Steam common directory escapes library")
        target = (common / name).resolve(strict=True)
        if not target.is_dir() or not _inside(target, common):
            raise ValueError("game directory escapes Steam common")
        build = state.get("buildid")
        build_id = build if isinstance(build, str) and build.isdecimal() else None
        title = state.get("name", name)
        if (
            not isinstance(title, str)
            or not 1 <= len(title.strip()) <= 500
            or any(ord(char) < 32 for char in title)
        ):
            raise ValueError("invalid Steam game name")
        flags = state.get("StateFlags")
        if flags is not None and (
            not isinstance(flags, str) or not flags.isdecimal() or not int(flags) & 4
        ):
            return None
        return {
            "name": title.strip(),
            "path": str(target),
            "app_id": app_id,
            "build_id": build_id,
            "running": state.get("Running") == "1",
            "updating": flags is not None and int(flags) != 4,
            # Pending/paused downloads (including missing/corrupt files) still lock
            # MOD writes, but do not perform disk work that blocks a plugin upgrade.
            # Unrecognized states remain conservative; this never grants MOD access.
            "update_active": flags is not None and bool(int(flags) & ~(2 | 4 | 32 | 128 | 512)),
        }

    def discover(self) -> list[dict]:
        """Keep catalog identities, then include other validated installed Steam titles."""
        libraries, issues = self._libraries()
        result: list[dict] = []
        roots = InstallationRoots()
        for original in self.catalog:
            found: dict | None = None
            for app_id in original["steam_app_ids"]:
                for library in libraries:
                    try:
                        candidate = self._installed(library, app_id)
                        if candidate:
                            found = candidate
                            break
                    except (OSError, UnicodeError, ValueError):
                        issues.append(f"{original['name']} 的 Steam 安装清单或目录无效")
                if found:
                    break
            base = {
                **copy.deepcopy(original),
                "installed": False,
                "path": None,
                "app_id": None,
                "build_id": None,
                "running": False,
                "updating": False,
            }
            if found:
                try:
                    if roots.register(Path(found["path"]), exclusive=True):
                        base = {**base, **found, "name": original["name"], "installed": True}
                    else:
                        issues.append(
                            "部分 Steam 游戏安装目录与其他游戏重叠，已跳过以保护 MOD 记录"
                        )
                except OSError:
                    issues.append("部分 Steam 游戏目录已变化，请刷新游戏库后重试")
            result.append(base)
        known = {app_id for game in self.catalog for app_id in game["steam_app_ids"]}
        manifests, scan_issues = manifest_candidates(libraries)
        issues.extend(scan_issues)
        for library, app_id in sorted(manifests, key=lambda item: (int(item[1]), str(item[0]))):
            if app_id in known:
                continue
            try:
                found = self._installed(library, app_id)
                if found is None or is_runtime_tool(app_id, found["name"]):
                    continue
                if not roots.register(Path(found["path"]), exclusive=True):
                    issues.append("部分 Steam 游戏安装目录与其他游戏重叠，已跳过以保护 MOD 记录")
                    continue
                result.append(
                    {
                        **discovered_entry(app_id, found["name"]),
                        **found,
                        "installed": True,
                    }
                )
                known.add(app_id)
            except (OSError, UnicodeError, ValueError):
                issues.append("部分 Steam 游戏安装清单或目录无效，已跳过")
        candidates = {game["app_id"]: Path(game["path"]) for game in result if game["installed"]}
        running, uncertain = _running_apps(candidates)
        if uncertain:
            issues.append("无法完整检查部分游戏进程；这些游戏暂时阻止安装以保护文件")
        result = [
            {
                **game,
                "running": game["running"]
                or game["app_id"] in running
                or game["app_id"] in uncertain,
            }
            for game in result
        ]
        self.issues = tuple(dict.fromkeys(issues))
        return result

    def discover_app(self, app_id: str) -> dict | None:
        """Validate exactly one pinned AppID when a reviewed row selects another variant."""
        if not valid_app_id(app_id):
            raise ModsError("Steam 游戏身份无效")
        libraries, issues = self._libraries()
        for library in libraries:
            try:
                found = self._installed(library, app_id)
                if found is None or is_runtime_tool(app_id, found["name"]):
                    continue
                running, uncertain = _running_apps({app_id: Path(found["path"])})
                return {
                    **found,
                    "running": found["running"] or app_id in running or app_id in uncertain,
                }
            except (OSError, UnicodeError, ValueError):
                issues.append("部分游戏的 Steam 安装清单或目录无效，已保留原身份记录")
        self.issues = tuple(dict.fromkeys([*self.issues, *issues]))
        return None

    def resolve_optional(self, game_id: str) -> dict | None:
        """Return an installed mapping, or None when Steam cannot validate it."""
        return next(
            (
                game
                for game in self.discover()
                if game["id"] == game_id and game["installed"] and not game.get("updating")
            ),
            None,
        )

    def resolve(self, game_id: str) -> dict:
        """Resolve a single installed game or raise a sanitized actionable error."""
        if (
            not isinstance(game_id, str)
            or not _APP_ID.fullmatch(game_id)
            and not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", game_id)
        ):
            raise ModsError("请选择有效的游戏")
        found = self.resolve_optional(game_id)
        if found is None:
            raise ModsError("未找到可验证的游戏安装目录，请先安装游戏并检查 Steam 存储设置")
        if found.get("updating"):
            raise ModsError("Steam 正在更新或验证游戏，请等待完成后重试")
        return found
