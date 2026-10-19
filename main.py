"""Decky lifecycle and explicit typed RPC surface for DeckyMods."""

import asyncio
import os
import pwd
import sys
from pathlib import Path
from typing import TypeVar

import decky

sys.path.insert(0, str(Path(__file__).resolve().parent / "py_modules"))

from decky_mods.errors import ModsError  # noqa: E402
from decky_mods.nxm import NxmHandler  # noqa: E402
from decky_mods.service import Service  # noqa: E402

_T = TypeVar("_T")


class Plugin:
    def __init__(self):
        self.service: Service | None = None
        self.receiver: asyncio.Task | None = None
        self.initial_error: str | None = None
        self._closing = False
        self._uninstall_requested = False
        self._uninstall_handler: NxmHandler | None = None

    async def _finish_worker(self, task: asyncio.Task[_T]) -> tuple[_T, bool]:
        cancelled = False
        while True:
            try:
                return await asyncio.shield(task), cancelled
            except asyncio.CancelledError:
                self._closing = True
                cancelled = True
                if task.cancelled():
                    raise

    async def _main(self) -> None:
        service: Service | None = None
        try:
            if self._closing:
                return
            if os.geteuid() == 0:
                raise ModsError("DeckyMods 应以普通 Deck 用户运行，请检查完整 ZIP 的无 root 标记")
            home = Path(getattr(decky, "DECKY_USER_HOME", pwd.getpwuid(os.getuid()).pw_dir))
            construction = asyncio.create_task(
                asyncio.to_thread(
                    Service,
                    Path(decky.DECKY_PLUGIN_DIR),
                    Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "backend",
                    home=home,
                )
            )
            service, cancelled = await self._finish_worker(construction)
            if cancelled:
                raise asyncio.CancelledError
            if self._closing:
                return
            recovery = asyncio.create_task(asyncio.to_thread(service.recover_all))
            _, cancelled = await self._finish_worker(recovery)
            if cancelled:
                raise asyncio.CancelledError
            if self._closing:
                return
            self.service = service
            service = None
            self.receiver = asyncio.create_task(self._receive(), name="DeckyMods NXM receiver")
        except ModsError as error:
            self.initial_error = str(error)
        except Exception:
            self.initial_error = "插件初始化失败，请检查安装包、普通用户权限及私有设置目录"
        finally:
            if service is not None:
                try:
                    self._uninstall_handler = service.handler
                    if self._uninstall_requested:
                        await self._uninstall()
                except Exception:
                    self.initial_error = "插件协议关联未能恢复，请重新加载插件后重试"
                finally:
                    try:
                        _, cancelled = await self._finish_worker(
                            asyncio.create_task(asyncio.to_thread(service.close))
                        )
                        if cancelled:
                            raise asyncio.CancelledError
                    except Exception:
                        self.initial_error = "插件初始化资源未能关闭，请重新加载插件后重试"

    async def _receive(self) -> None:
        while True:
            try:
                if self.service:
                    await asyncio.to_thread(self.service.poll_inbox)
                    if await asyncio.to_thread(self.service.updates.check_due):
                        await asyncio.to_thread(self.service.check_update)
            except ModsError as error:
                if self.service:
                    self.service.error = str(error)
            except Exception:
                if self.service:
                    self.service.error = "下载接收暂不可用；请检查设置或使用本地压缩包导入"
            await asyncio.sleep(2)

    async def _unload(self) -> None:
        self._closing = True
        if self.receiver:
            self.receiver.cancel()
            try:
                await self.receiver
            except asyncio.CancelledError:
                pass
            self.receiver = None
        service, self.service = self.service, None
        if service:
            self._uninstall_handler = service.handler
            await asyncio.to_thread(service.close)

    async def _uninstall(self) -> None:
        self._uninstall_requested = True
        handler = self.service.handler if self.service else self._uninstall_handler
        if handler and handler.status()["enabled"]:
            await asyncio.to_thread(handler.set_enabled, False)

    async def _call(self, method: str, *args) -> dict:
        if self._closing:
            return {"ok": False, "error": "插件已卸载，请重新打开插件后重试"}
        if self.service is None:
            return {"ok": False, "error": self.initial_error or "插件正在初始化，请稍后重试"}
        try:
            return {
                "ok": True,
                "data": await asyncio.to_thread(getattr(self.service, method), *args),
            }
        except ModsError as error:
            return {"ok": False, "error": str(error)}
        except Exception:
            return {"ok": False, "error": "操作未完成，请检查磁盘、权限和网络后重试；请勿删除备份"}

    async def get_status(self) -> dict:
        return await self._call("get_status")

    async def list_games(self) -> dict:
        return await self._call("list_games")

    async def get_game(self, game_id: str) -> dict:
        return await self._call("get_game", game_id)

    async def get_mod_details(self, game_id: str, mod_id: str) -> dict:
        return await self._call("get_mod_details", game_id, mod_id)

    async def set_game_root(self, game_id: str, mode: str, path: str = "") -> dict:
        return await self._call("set_game_root", game_id, mode, path)

    async def get_launch_setup(self, game_id: str) -> dict:
        return await self._call("get_launch_setup", game_id)

    async def get_resident_status(self, game_id: str) -> dict:
        return await self._call("get_resident_status", game_id)

    async def prepare_resident_settings(self, game_id: str, enable_pak: bool) -> dict:
        return await self._call("prepare_resident_settings", game_id, enable_pak)

    async def restore_resident_settings(self, game_id: str) -> dict:
        return await self._call("restore_resident_settings", game_id)

    async def get_update_status(self) -> dict:
        return await self._call("get_update_status")

    async def get_install_guide(self, game_id: str) -> dict:
        return await self._call("get_install_guide", game_id)

    async def set_update_options(self, source: str, auto_check: bool) -> dict:
        return await self._call("set_update_options", source, auto_check)

    async def check_update(self) -> dict:
        return await self._call("check_update")

    async def prepare_update(self) -> dict:
        return await self._call("prepare_update")

    async def set_launch_auto(self, game_id: str, enabled: bool) -> dict:
        return await self._call("set_launch_auto", game_id, enabled)

    async def prepare_launch_options(
        self, game_id: str, current: str, restore: bool = False
    ) -> dict:
        return await self._call("prepare_launch_options", game_id, current, restore)

    async def finish_launch_options(self, game_id: str, change_id: str, observed: str) -> dict:
        return await self._call("finish_launch_options", game_id, change_id, observed)

    async def bind_account(self, api_key: str) -> dict:
        return await self._call("bind_account", api_key)

    async def disconnect_account(self) -> dict:
        return await self._call("disconnect_account")

    async def resolve_mod(self, game_id: str, reference: str) -> dict:
        return await self._call("resolve_mod", game_id, reference)

    async def begin_download(
        self, game_id: str, mod_id: int, file_id: int, install_mode: str = "auto"
    ) -> dict:
        return await self._call("begin_download", game_id, mod_id, file_id, install_mode)

    async def accept_nxm(
        self, uri: str, install_mode: str = "auto", expected_game_id: str | None = None
    ) -> dict:
        return await self._call("accept_nxm", uri, install_mode, expected_game_id)

    async def import_archive(
        self, game_id: str, path: str, name: str, install_mode: str = "auto"
    ) -> dict:
        return await self._call("import_archive", game_id, path, name, install_mode)

    async def get_import_directory(self) -> dict:
        return await self._call("get_import_directory")

    async def get_plan(self, plan_id: str) -> dict:
        return await self._call("get_plan", plan_id)

    async def install_plan(self, plan_id: str, allow_conflicts: bool) -> dict:
        return await self._call("install_plan", plan_id, allow_conflicts)

    async def set_mod_enabled(self, game_id: str, mod_id: str, enabled: bool) -> dict:
        return await self._call("set_mod_enabled", game_id, mod_id, enabled)

    async def uninstall_mod(self, game_id: str, mod_id: str) -> dict:
        return await self._call("uninstall_mod", game_id, mod_id)

    async def get_jobs(self) -> dict:
        return await self._call("get_jobs")

    async def cancel_job(self, job_id: str) -> dict:
        return await self._call("cancel_job", job_id)

    async def set_nxm_handler(self, enabled: bool) -> dict:
        return await self._call("set_nxm_handler", enabled)
