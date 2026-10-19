"""SQLite commits metadata and recovery intent with full durability."""

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .errors import ModsError
from .paths import private_directory


class Database:
    def __init__(self, directory: Path):
        private_directory(directory)
        self.path = directory / "state.sqlite3"
        if self.path.is_symlink():
            raise ModsError("状态库不能是符号链接")
        with self.connection() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS games(id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS plans(id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS transactions(
                    id TEXT PRIMARY KEY, game_id TEXT NOT NULL, phase TEXT NOT NULL,
                    data TEXT NOT NULL, error TEXT);
            """)
        self.path.chmod(0o600)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        try:
            connection = sqlite3.connect(self.path, timeout=15)
            connection.execute("PRAGMA synchronous=FULL")
            try:
                with connection:
                    yield connection
            finally:
                connection.close()
        except (sqlite3.DatabaseError, ValueError) as error:
            raise ModsError("状态库无法安全读取，请保留设置目录并检查磁盘") from error

    def game(self, game_id: str) -> dict | None:
        with self.connection() as connection:
            row = connection.execute("SELECT data FROM games WHERE id=?", (game_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def plan(self, plan_id: str) -> dict:
        with self.connection() as connection:
            row = connection.execute("SELECT data FROM plans WHERE id=?", (plan_id,)).fetchone()
        if row is None:
            raise ModsError("安装预览已失效，请重新导入压缩包")
        return json.loads(row[0])

    def save_plan(self, plan: dict) -> None:
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO plans(id,data) VALUES (?,?)", (plan["id"], json.dumps(plan))
            )

    def pending(self, game_id: str) -> list[dict]:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT data FROM transactions WHERE game_id=? "
                "AND phase IN ('applying','recovery') ORDER BY rowid DESC",
                (game_id,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def begin(self, operation: dict) -> None:
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO transactions(id,game_id,phase,data) VALUES (?,?,'applying',?)",
                (operation["id"], operation["game_id"], json.dumps(operation)),
            )

    def finish(self, operation: dict, state: dict, *, committed: bool) -> None:
        with self.connection() as connection:
            if committed:
                connection.execute(
                    "INSERT INTO games(id,data) VALUES (?,?) "
                    "ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                    (operation["game_id"], json.dumps(state)),
                )
                plan_id = operation.get("plan_id")
                if plan_id:
                    connection.execute("DELETE FROM plans WHERE id=?", (plan_id,))
            connection.execute(
                "UPDATE transactions SET phase=?,error=NULL WHERE id=?",
                ("committed" if committed else "rolled_back", operation["id"]),
            )

    def failed_recovery(self, operation: dict) -> None:
        with self.connection() as connection:
            connection.execute(
                "UPDATE transactions SET phase='recovery',error=? WHERE id=?",
                ("文件被外部修改或存储设备不可用，恢复尚未完成", operation["id"]),
            )

    def rewrite(self, operation: dict) -> None:
        with self.connection() as connection:
            connection.execute(
                "UPDATE transactions SET data=? WHERE id=?",
                (json.dumps(operation), operation["id"]),
            )
