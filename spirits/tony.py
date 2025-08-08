"""Tony companion module."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".letsgo" / "spirits.db"


def _ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tony (ts TEXT, msg TEXT)"
        )
        conn.commit()


def record(text: str) -> None:
    """Persist ``text`` in the tony table."""
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO tony (ts, msg) VALUES (?, ?)",
            (datetime.utcnow().isoformat(), text),
        )
        conn.commit()


def start_chat(last_cmd: str) -> str:
    """Return the initial message when deep chat starts."""
    return f"Diving deep into '{last_cmd}'. Here's the breakdown."


def chat(message: str) -> str:
    """Echo-style deep explanation."""
    return f"Tony: {message}"
