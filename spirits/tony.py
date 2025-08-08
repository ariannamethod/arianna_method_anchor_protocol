from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3


@dataclass
class Companion:
    """Deep explaining companion logging everything to SQLite."""

    name: str = "tony"

    def __post_init__(self) -> None:
        data_dir = Path.home() / ".letsgo"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / f"{self.name}.sqlite"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS log (ts TEXT, role TEXT, message TEXT)"
        )
        self.conn.commit()

    def record(self, role: str, message: str) -> None:
        self.conn.execute(
            "INSERT INTO log VALUES (?, ?, ?)",
            (datetime.utcnow().isoformat(), role, message),
        )
        self.conn.commit()

    def start(self, last_command: str) -> str:
        reply = f"похоже, команда '{last_command}' вызвала вопросы. погружаемся глубже."
        self.record("system", reply)
        return reply

    def stop(self) -> str:
        reply = "xplainer disengaged."
        self.record("system", reply)
        return reply

    def respond(self, text: str) -> str:
        self.record("user", text)
        reply = f"tony: {text}"
        self.record("assistant", reply)
        return reply
