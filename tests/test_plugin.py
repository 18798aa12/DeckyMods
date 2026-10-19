import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from decky_mods.errors import ModsError


@pytest.fixture
def plugin(monkeypatch, tmp_path):
    monkeypatch.setitem(
        sys.modules,
        "decky",
        SimpleNamespace(
            DECKY_PLUGIN_DIR=str(Path(__file__).resolve().parents[1]),
            DECKY_PLUGIN_SETTINGS_DIR=str(tmp_path / "settings"),
            DECKY_USER_HOME=str(tmp_path / "home"),
        ),
    )
    spec = importlib.util.spec_from_file_location(
        "mods_plugin", Path(__file__).resolve().parents[1] / "main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Plugin()


async def test_rpc_returns_data_and_sanitizes_unexpected_errors(plugin):
    class Fake:
        def get_status(self):
            return {"version": "0.1.0"}

        def bind_account(self, value):
            raise RuntimeError("private-api-key")

        def get_game(self, value):
            raise ModsError("请选择已安装游戏")

    plugin.service = Fake()
    assert await plugin.get_status() == {"ok": True, "data": {"version": "0.1.0"}}
    assert "private-api-key" not in str(await plugin.bind_account("private-api-key"))
    assert await plugin.get_game("missing") == {"ok": False, "error": "请选择已安装游戏"}


async def test_uninitialized_backend_returns_safe_error(plugin):
    result = await plugin.list_games()
    assert result["ok"] is False
    assert "初始化" in result["error"]


def test_all_frontend_rpc_names_exist(plugin):
    source = (Path(__file__).resolve().parents[1] / "src/rpc.ts").read_text()
    import re

    methods = re.findall(r'"([a-z]+(?:_[a-z]+)+)"', source)
    assert len(methods) >= 16
    assert all(callable(getattr(plugin, name, None)) for name in methods)


@pytest.mark.parametrize("prepared", [False, True])
async def test_native_uninstall_restores_handler_but_preserves_account_preferences(
    plugin, prepared
):
    calls = []

    class Handler:
        def status(self):
            return {"enabled": True}

        def set_enabled(self, enabled):
            calls.append(enabled)

    class Fake:
        handler = Handler()
        updates = SimpleNamespace(installation_pending=lambda: prepared)

        def disconnect_account(self):
            calls.append("account removed")

    plugin.service = Fake()
    await plugin._uninstall()
    assert calls == [False]


async def test_background_update_deadline_checks_run_off_the_event_loop(plugin):
    import asyncio
    import threading

    observed = []
    main_thread = threading.get_ident()

    class Fake:
        error = None

        def poll_inbox(self):
            pass

        def deadline(self):
            observed.append(threading.get_ident())
            return False

    instance = Fake()
    instance.updates = SimpleNamespace(check_due=instance.deadline)
    plugin.service = instance
    receiver = asyncio.create_task(plugin._receive())
    for _ in range(100):
        if observed:
            break
        await asyncio.sleep(0.001)
    receiver.cancel()
    with pytest.raises(asyncio.CancelledError):
        await receiver
    assert observed and observed[0] != main_thread
