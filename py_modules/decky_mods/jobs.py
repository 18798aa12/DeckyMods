"""Bounded background jobs; persisted public snapshots never contain download grants."""

import json
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, wait
from pathlib import Path

from .errors import ModsError
from .paths import atomic_write, private_directory

PUBLIC_FIELDS = (
    "id",
    "game_id",
    "name",
    "phase",
    "bytes_done",
    "bytes_total",
    "error",
    "plan_id",
    "browser_url",
)
TERMINAL = {"ready", "complete", "failed", "cancelled", "awaiting_browser"}


class Jobs:
    def __init__(self, directory: Path):
        private_directory(directory)
        self.path = directory / "jobs.json"
        self.lock = threading.RLock()
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="DeckyMods")
        self.rows: dict[str, dict] = {}
        self.events: dict[str, threading.Event] = {}
        self.futures: dict[str, Future] = {}
        self.closed = False
        self.last_saved = 0.0
        try:
            if self.path.exists():
                if self.path.is_symlink() or self.path.stat().st_size > 1024**2:
                    raise ValueError
                rows = json.loads(self.path.read_text())
                if not isinstance(rows, list):
                    raise ValueError
                for row in rows:
                    if not isinstance(row, dict) or not all(key in row for key in PUBLIC_FIELDS):
                        raise ValueError
                    if row["phase"] not in TERMINAL:
                        row = {
                            **row,
                            "phase": "failed",
                            "error": "上次任务被中断，原文件与备份保留；请重试",
                        }
                    self.rows[row["id"]] = row
        except (OSError, ValueError) as error:
            raise ModsError("下载任务记录无法读取，请保留私有设置目录后检查磁盘") from error

    @staticmethod
    def public(row: dict) -> dict:
        return {key: row[key] for key in PUBLIC_FIELDS}

    def _save(self) -> None:
        atomic_write(self.path, json.dumps(list(self.rows.values()), ensure_ascii=False).encode())
        self.last_saved = time.monotonic()

    def create(self, game_id: str, name: str, phase: str = "queued", **fields) -> dict:
        with self.lock:
            if (
                self.closed
                or sum(
                    row["phase"] not in {"complete", "cancelled", "failed"}
                    for row in self.rows.values()
                )
                >= 16
            ):
                raise ModsError("任务队列已满，请先完成或取消已有任务")
            if len(self.rows) >= 100:
                removable = [
                    key
                    for key, row in self.rows.items()
                    if row["phase"] in {"complete", "cancelled", "failed"}
                ]
                self.rows = {
                    key: row for key, row in self.rows.items() if key not in removable[:20]
                }
            row = {
                "id": uuid.uuid4().hex,
                "game_id": game_id,
                "name": name,
                "phase": phase,
                "bytes_done": 0,
                "bytes_total": 0,
                "error": None,
                "plan_id": None,
                "browser_url": None,
                **fields,
            }
            self.rows = {**self.rows, row["id"]: row}
            self.events[row["id"]] = threading.Event()
            self._save()
            return self.public(row)

    def get(self, ident: str) -> dict:
        with self.lock:
            if not isinstance(ident, str) or ident not in self.rows:
                raise ModsError("任务不存在，请刷新列表")
            return dict(self.rows[ident])

    def list(self) -> list[dict]:
        with self.lock:
            return [self.public(row) for row in reversed(self.rows.values())]

    def update(self, ident: str, **fields) -> dict:
        with self.lock:
            previous = self.get(ident)
            if previous["phase"] == "cancelled":
                return self.public(previous)
            row = {**previous, **fields}
            self.rows = {**self.rows, ident: row}
            if previous["phase"] != row["phase"] or time.monotonic() - self.last_saved >= 1:
                self._save()
            return self.public(row)

    def start(
        self,
        ident: str,
        operation: Callable[[threading.Event], None],
        *,
        transition: tuple[str, str] | None = None,
    ) -> dict:
        with self.lock:
            if self.closed:
                raise ModsError("插件正在关闭，请重新打开后重试")
            previous = self.futures.get(ident)
            if transition:
                if self.get(ident)["phase"] != transition[0]:
                    raise ModsError("任务状态已变化，请刷新后重试")
                self.update(ident, phase=transition[1])
            elif previous and not previous.done():
                raise ModsError("该任务仍在处理，请稍候")
            cancel = self.events.setdefault(ident, threading.Event())

            def run() -> None:
                try:
                    # A scan may publish ready just before its Future finishes.
                    # Chain installation after it instead of leaving a stuck job.
                    if previous:
                        previous.result()
                    if cancel.is_set():
                        raise ModsError("任务已取消")
                    operation(cancel)
                except ModsError as error:
                    self.update(
                        ident, phase="cancelled" if cancel.is_set() else "failed", error=str(error)
                    )
                except Exception:
                    self.update(
                        ident,
                        phase="failed",
                        error="任务失败，原游戏文件和已保存备份保留；请检查磁盘后重试",
                    )

            self.futures[ident] = self.pool.submit(run)
            return self.public(self.get(ident))

    def cancel(self, ident: str) -> dict:
        with self.lock:
            row = self.get(ident)
            if row["phase"] in {"installing", "complete"}:
                raise ModsError("安装已开始或任务已完成，请等待并在 MOD 列表管理")
            self.events.setdefault(ident, threading.Event()).set()
            return self.update(ident, phase="cancelled", error=None, browser_url=None)

    def close(self) -> None:
        with self.lock:
            self.closed = True
            for ident, event in self.events.items():
                if self.rows.get(ident, {}).get("phase") != "installing":
                    event.set()
            futures = list(self.futures.values())
        wait(futures, timeout=12)
        self.pool.shutdown(wait=False, cancel_futures=True)
