"""Public application operations; no client-supplied deployment paths."""

import platform
import shutil
import threading
import uuid
from pathlib import Path

from ._nexus_private import read_json, write_json
from .adapters import plan_files
from .archive import extract_archive
from .catalog import load_catalog
from .deployment import Deployment
from .errors import ModsError
from .game_identities import GameIdentities
from .game_roots import GameRoots
from .gamefs import fingerprint
from .imports import LocalArchives
from .install_guides import InstallGuides
from .jobs import Jobs
from .launch_options import LaunchOptions
from .mod_details import ModDetails
from .nexus import NexusClient
from .nxm import NxmHandler
from .paths import private_directory
from .profile_install import plan_profile
from .re_setup import LOOSE_KEY, MODERN, PAK_KEY, RESettings
from .root_install import plan_root_files
from .steam import SteamDiscovery
from .update_feed import GITHUB_SOURCE
from .updates import UpdateManager


class Service:
    def __init__(
        self,
        plugin_dir: Path,
        directory: Path,
        *,
        home: Path | None = None,
        discovery=None,
        nexus=None,
        handler=None,
    ):
        self.plugin_dir, self.directory = plugin_dir, directory
        self.home = (home or Path.home()).resolve()
        private_directory(directory)
        self.discovery = discovery or SteamDiscovery(load_catalog(plugin_dir), self.home)
        self.engine = Deployment(directory / "deployment")
        self.jobs = Jobs(directory / "tasks")
        identities = GameIdentities(
            directory / "game-identities",
            self.discovery,
            self.engine.db,
            self.jobs,
            directory / "game-roots/roots.json",
        )
        self.roots = GameRoots(directory / "game-roots", identities, self.home)
        self.nexus = nexus or NexusClient(directory / "account")
        self.handler = handler or NxmHandler(directory / "receiver", plugin_dir, self.home)
        receiver_preference = read_json(directory / "receiver-preferences.json") or {}
        if receiver_preference.get("enabled") is True:
            self.handler.set_enabled(True)
        self.mod_details = ModDetails(directory / "mod-details", self.nexus)
        self.archives = LocalArchives(self.home)
        self.install_guides = InstallGuides(plugin_dir)
        self.launch_options = LaunchOptions(directory / "launch-options")
        self.resident = RESettings(directory / "resident-settings")
        self.updates = UpdateManager(
            plugin_dir, directory / "updates", "0.3.0", source=GITHUB_SOURCE
        )
        self.downloads = directory / "downloads"
        private_directory(self.downloads)
        self.lock = threading.RLock()
        self.recovery_errors: dict[str, str] = {}
        self.error: str | None = None

    def get_status(self) -> dict:
        return {
            "version": "0.3.0",
            "platform_supported": platform.system() == "Linux",
            "auth": self.nexus.status(),
            "jobs": self.get_jobs(),
            "handler": self.handler.status(),
            "error": self.error,
        }

    def list_games(self) -> list[dict]:
        return self.roots.discover()

    def set_game_root(self, game_id: str, mode: str, path: str = "") -> dict:
        with self.lock, self.engine.lock:
            if game_id in self.recovery_errors:
                raise ModsError("请先解决 MOD 恢复问题，再改变游戏目录")
            if any(
                job["game_id"] == game_id
                and job["phase"] not in {"complete", "failed", "cancelled"}
                for job in self.get_jobs()
            ):
                raise ModsError("请先完成或取消此游戏的 MOD 任务，再改变目录")
            state = self.engine.db.game(game_id)
            if state and state["mods"]:
                raise ModsError("此游戏已有管理中的 MOD；请先卸载这些 MOD，再改变目录")
            self.roots.configure(game_id, mode, path)
            return self.get_game(game_id)

    def get_game(self, game_id: str) -> dict:
        matches = [game for game in self.list_games() if game["id"] == game_id]
        if not matches:
            raise ModsError("未找到所选游戏，请刷新 Steam 游戏库后重试")
        return {
            "game": matches[0],
            "mods": self.engine.list_mods(game_id),
            "recovery_error": self.recovery_errors.get(game_id),
        }

    def bind_account(self, api_key: str) -> dict:
        return self.nexus.bind(api_key)

    def get_mod_details(self, game_id: str, mod_id: str) -> dict:
        game = self.get_game(game_id)["game"]
        with self.engine.lock:
            state = self.engine.db.game(game_id)
            mods = [mod for mod in (state or {}).get("mods", []) if mod["id"] == mod_id]
            if not mods:
                raise ModsError("MOD 已卸载或不存在，请刷新列表")
            mod = dict(mods[0])
        return self.mod_details.get(game, mod)

    def get_install_guide(self, game_id: str) -> dict:
        return self.install_guides.for_game(self.get_game(game_id)["game"])

    def _install_mode(self, game: dict, mode: str) -> str:
        if isinstance(mode, str) and mode.startswith("method:"):
            self.install_guides.resolve_mode(game, mode)
            return mode
        if not isinstance(mode, str) or mode not in {"auto", "game_root"}:
            raise ModsError("安装模式无效，请重新选择")
        if mode == "game_root" and game["adapter"] != "catalog":
            raise ModsError("已适配游戏请使用其专用安装规则")
        return mode

    def get_resident_status(self, game_id: str) -> dict:
        with self.lock:
            return self.resident.status(self.get_game(game_id)["game"])

    def prepare_resident_settings(self, game_id: str, enable_pak: bool) -> dict:
        if type(enable_pak) is not bool:
            raise ModsError("资源加载选项必须为布尔值")
        with self.lock:
            if game_id in self.recovery_errors:
                raise ModsError("请先解决 MOD 文件恢复问题，再配置前置")
            keys = [LOOSE_KEY, *([PAK_KEY] if enable_pak else [])]
            return self.resident.apply(self.roots.resolve(game_id), keys)

    def restore_resident_settings(self, game_id: str) -> dict:
        with self.lock, self.engine.lock:
            state = self.engine.db.game(game_id)
            if any(
                mod["enabled"]
                and any(
                    file["target"].casefold().startswith(("natives/", "pak_mods/"))
                    for file in mod["files"]
                )
                for mod in (state or {}).get("mods", [])
            ):
                raise ModsError("请先禁用依赖资源加载器的 MOD，再恢复前置配置")
            return self.resident.restore(self.roots.resolve(game_id))

    def get_update_status(self) -> dict:
        return self.updates.status()

    def set_update_options(self, source: str, auto_check: bool) -> dict:
        return self.updates.configure(source, auto_check)

    def check_update(self) -> dict:
        return self.updates.check()

    def prepare_update(self) -> dict:
        with self.lock:
            if any(
                game.get("running") or game.get("update_active", game.get("updating"))
                for game in self.list_games()
            ):
                raise ModsError("请退出游戏并等待 Steam 更新完成，再安装插件更新")
            if any(
                job["phase"] in {"scanning", "downloading", "installing", "queued"}
                for job in self.get_jobs()
            ):
                raise ModsError("请先完成或取消 MOD 任务，再更新插件")
            return self.updates.prepare()

    def _prepare_resource_flags(self, game: dict, files: list[dict]) -> None:
        if game["id"] not in MODERN:
            return
        targets = [entry["target"].casefold() for entry in files]
        keys = []
        if any(target.startswith(("natives/", "pak_mods/")) for target in targets):
            keys.append(LOOSE_KEY)
        if any(target.startswith("pak_mods/") for target in targets):
            keys.append(PAK_KEY)
        if keys:
            self.resident.apply(game, keys)

    def get_launch_setup(self, game_id: str) -> dict:
        with self.lock:
            return self.launch_options.status(self.get_game(game_id)["game"])

    def set_launch_auto(self, game_id: str, enabled: bool) -> dict:
        with self.lock:
            return self.launch_options.set_auto(self.get_game(game_id)["game"], enabled)

    def prepare_launch_options(self, game_id: str, current: str, restore: bool = False) -> dict:
        with self.lock:
            game = self.roots.resolve(game_id)
            if game_id in self.recovery_errors:
                raise ModsError("请先解决游戏文件恢复问题，再配置启动项")
            return self.launch_options.prepare(game, current, restore)

    def finish_launch_options(self, game_id: str, change_id: str, observed: str) -> dict:
        with self.lock:
            game = self.roots.resolve(game_id)
            return self.launch_options.finish(game, change_id, observed)

    def disconnect_account(self) -> dict:
        return self.nexus.disconnect()

    def resolve_mod(self, game_id: str, reference: str) -> dict:
        game = self.get_game(game_id)["game"]
        if not game.get("nexus_domain"):
            raise ModsError("此游戏尚无已核实的 Nexus 映射，请按作者说明使用本地 ZIP 压缩包")
        return {**self.nexus.resolve(game["nexus_domain"], reference), "game_id": game_id}

    def begin_download(
        self, game_id: str, mod_id: int, file_id: int, install_mode: str = "auto"
    ) -> dict:
        game = self.roots.resolve(game_id)
        if not game.get("nexus_domain"):
            raise ModsError("此游戏尚无已核实的 Nexus 映射，请按作者说明使用本地 ZIP 压缩包")
        mode = self._install_mode(game, install_mode)
        info = self.nexus.resolve(game["nexus_domain"], str(mod_id))
        files = [file for file in info["files"] if file["file_id"] == file_id]
        if not files:
            raise ModsError("所选文件不属于这个 MOD，请重新查询文件列表")
        with self.lock:
            for job in self.jobs.list():
                private = self.jobs.get(job["id"])
                if (
                    private.get("identity") == {"mod_id": mod_id, "file_id": file_id}
                    and job["game_id"] == game_id
                    and job["phase"] not in {"failed", "cancelled", "complete"}
                ):
                    if private.get("install_mode", "auto") != mode:
                        raise ModsError("此文件已有其他安装模式的任务，请先完成或取消原任务")
                    return job
            job = self.jobs.create(
                game_id,
                info["name"][:120],
                identity={"mod_id": mod_id, "file_id": file_id},
                install_mode=mode,
            )
            if not self.nexus.status()["premium"]:
                return self.jobs.update(
                    job["id"],
                    phase="awaiting_browser",
                    browser_url=self.nexus.browser_url(game["nexus_domain"], mod_id, file_id),
                )
            return self._download(job["id"], game, mod_id, file_id)

    def accept_nxm(
        self, uri: str, install_mode: str = "auto", expected_game_id: str | None = None
    ) -> dict:
        grant = self.nexus.parse_nxm(uri)
        if not isinstance(install_mode, str) or (
            install_mode not in {"auto", "game_root"} and not install_mode.startswith("method:")
        ):
            raise ModsError("安装模式无效，请重新选择")
        if install_mode != "auto":
            if not expected_game_id:
                raise ModsError("根目录安装必须先选择游戏")
            selected = self.roots.resolve(expected_game_id)
            self._install_mode(selected, install_mode)
            if selected["nexus_domain"] != grant["domain"]:
                raise ModsError("NXM 链接与所选游戏不同，请切换到对应游戏")
        with self.lock:
            discovered = self.list_games()
            by_id = {game["id"]: game for game in discovered}
            matches = [
                job
                for job in self.jobs.list()
                if job["phase"] not in {"failed", "cancelled", "complete"}
                and self.jobs.get(job["id"]).get("identity")
                == {"mod_id": grant["mod_id"], "file_id": grant["file_id"]}
                and by_id.get(job["game_id"], {}).get("nexus_domain") == grant["domain"]
            ]
            if len(matches) > 1:
                raise ModsError("此文件对应多个游戏任务，请先取消多余任务再确认下载")
            if matches:
                job = matches[0]
                if install_mode != "auto" and (
                    job["game_id"] != expected_game_id
                    or self.jobs.get(job["id"]).get("install_mode", "auto") != install_mode
                ):
                    raise ModsError("此下载任务的安装模式不同，请先取消原任务")
                if job["phase"] != "awaiting_browser":
                    return job
                game = self.roots.resolve(job["game_id"])
            else:
                games = [
                    game
                    for game in discovered
                    if game["nexus_domain"] == grant["domain"] and game["installed"]
                ]
                if len(games) != 1:
                    raise ModsError("请先在插件选择已安装游戏，并从 MOD 文件列表开始下载")
                game = self.roots.resolve(games[0]["id"])
                info = self.nexus.resolve(game["nexus_domain"], str(grant["mod_id"]))
                if not any(file["file_id"] == grant["file_id"] for file in info["files"]):
                    raise ModsError("网页授权的文件不在当前 MOD 文件列表中")
                job = self.jobs.create(
                    game["id"],
                    info["name"][:120],
                    identity={"mod_id": grant["mod_id"], "file_id": grant["file_id"]},
                    install_mode=install_mode,
                )
            return self._download(job["id"], game, grant["mod_id"], grant["file_id"], uri)

    def _download(
        self, ident: str, game: dict, mod_id: int, file_id: int, uri: str | None = None
    ) -> dict:
        self.jobs.update(ident, phase="downloading", browser_url=None)
        archive = self.downloads / (ident + ".archive")

        def action(cancel: threading.Event) -> None:
            try:
                self.nexus.download(
                    game["nexus_domain"],
                    mod_id,
                    file_id,
                    archive,
                    cancel,
                    lambda done, total: self.jobs.update(ident, bytes_done=done, bytes_total=total),
                    uri,
                )
                identity = {
                    "mod_id": mod_id,
                    "file_id": file_id,
                    "source_url": f"https://www.nexusmods.com/{game['nexus_domain']}/mods/{mod_id}",
                }
                self._scan(ident, archive, identity, cancel)
            finally:
                archive.unlink(missing_ok=True)

        return self.jobs.start(ident, action)

    def import_archive(
        self, game_id: str, path: str, name: str, install_mode: str = "auto"
    ) -> dict:
        mode = self._install_mode(self.roots.resolve(game_id), install_mode)
        source = self.archives.validate(path)
        label = name.strip() if isinstance(name, str) and name.strip() else source.stem[:120]
        if len(label) > 120:
            raise ModsError("MOD 名称不能超过 120 个字符")
        job = self.jobs.create(game_id, label, install_mode=mode, archive_name=source.name)
        archive = self.downloads / (job["id"] + source.suffix.lower())

        def action(cancel: threading.Event) -> None:
            try:
                self.jobs.update(job["id"], phase="scanning")
                self.archives.copy(source, archive, cancel)
                self._scan(job["id"], archive, None, cancel)
            finally:
                archive.unlink(missing_ok=True)

        return self.jobs.start(job["id"], action)

    def get_import_directory(self) -> str:
        return self.archives.start_directory()

    def _scan(
        self, ident: str, archive: Path, identity: dict | None, cancel: threading.Event
    ) -> None:
        self.jobs.update(ident, phase="scanning")
        extracted = self.directory / ("staging-" + uuid.uuid4().hex)
        try:
            extract_archive(archive, extracted, cancel=cancel)
            if cancel.is_set():
                raise ModsError("任务已取消")
            job = self.jobs.get(ident)
            game = self.roots.resolve(job["game_id"])
            mode = self._install_mode(game, job.get("install_mode", "auto"))
            if mode.startswith("method:"):
                mapping = plan_profile(
                    game, extracted, self.install_guides.resolve_mode(game, mode)
                )
            else:
                mapping = (
                    plan_root_files(game, extracted)
                    if mode == "game_root"
                    else plan_files(game, extracted)
                )
            metadata = self.mod_details.capture(
                extracted, identity, job.get("archive_name", ""), game
            )
            plan = self.engine.prepare(
                game, job["name"], extracted, mapping, {**(identity or {}), "details": metadata}
            )
            if cancel.is_set():
                raise ModsError("任务已取消")
            self.jobs.update(ident, phase="ready", plan_id=plan["id"], error=None)
        finally:
            if extracted.exists():
                shutil.rmtree(extracted)

    def get_plan(self, plan_id: str) -> dict:
        return self.engine.get_plan(plan_id)

    def install_plan(self, plan_id: str, allow_conflicts: bool) -> dict:
        if type(allow_conflicts) is not bool:
            raise ModsError("覆盖确认必须为布尔值")
        with self.lock:
            matches = [job for job in self.jobs.list() if job["plan_id"] == plan_id]
            if not matches:
                raise ModsError("安装任务已失效，请重新导入")
            job = matches[0]
            if job["phase"] == "installing":
                return job
            if job["phase"] != "ready":
                raise ModsError("此任务不能安装，请重新导入")
            plan = self.engine.get_plan(plan_id)
            if not plan["can_install"]:
                raise ModsError(plan["blocked_reason"])
            if plan["conflicts"] and not allow_conflicts:
                raise ModsError("请先确认覆盖冲突")
            game = self.roots.resolve(job["game_id"])

            def action(cancel: threading.Event) -> None:
                with self.engine.lock:
                    current = self.roots.resolve(game["id"])
                    private = self.engine.db.plan(plan_id)
                    if private["fingerprint"] != fingerprint(current):
                        raise ModsError("游戏或版本变化，请重新生成安装预览")
                    self._prepare_resource_flags(current, private["mod"]["files"])
                    self.engine.install(current, plan_id, allow_conflicts)
                self.jobs.update(job["id"], phase="complete", error=None)

            return self.jobs.start(job["id"], action, transition=("ready", "installing"))

    def set_mod_enabled(self, game_id: str, mod_id: str, enabled: bool) -> dict:
        if type(enabled) is not bool:
            raise ModsError("启用状态必须为布尔值")
        with self.engine.lock:
            game = self.roots.resolve(game_id)
            if enabled:
                state = self.engine.db.game(game_id)
                matches = [mod for mod in (state or {}).get("mods", []) if mod["id"] == mod_id]
                if matches:
                    self._prepare_resource_flags(game, matches[0]["files"])
            self.engine.set_enabled(game, mod_id, enabled)
            return self.get_game(game_id)

    def uninstall_mod(self, game_id: str, mod_id: str) -> dict:
        self.engine.uninstall(self.roots.resolve(game_id), mod_id)
        return self.get_game(game_id)

    def get_jobs(self) -> list[dict]:
        return self.jobs.list()

    def cancel_job(self, job_id: str) -> dict:
        return self.jobs.cancel(job_id)

    def set_nxm_handler(self, enabled: bool) -> dict:
        result = self.handler.set_enabled(enabled)
        write_json(self.directory / "receiver-preferences.json", {"enabled": enabled})
        return result

    def poll_inbox(self) -> None:
        for uri in self.handler.drain():
            try:
                self.accept_nxm(uri)
            except ModsError as error:
                self.error = str(error)

    def recover_all(self) -> None:
        for game in self.list_games():
            if game["installed"]:
                try:
                    if not game["running"] and not game.get("updating"):
                        self.engine.recover(game)
                        self.resident.engine.recover(game)
                        self.recovery_errors = {
                            ident: error
                            for ident, error in self.recovery_errors.items()
                            if ident != game["id"]
                        }
                except ModsError as error:
                    self.recovery_errors = {**self.recovery_errors, game["id"]: str(error)}

    def close(self) -> None:
        self.jobs.close()
        self.handler.close()
