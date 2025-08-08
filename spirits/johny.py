"""Johny companion module."""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".letsgo" / "spirits.db"


def _ensure_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS johny (ts TEXT, msg TEXT)"
        )
        conn.commit()


def record(text: str) -> None:
    """Persist ``text`` in the johny table."""
    _ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO johny (ts, msg) VALUES (?, ?)",
            (datetime.utcnow().isoformat(), text),
        )
        conn.commit()


def start_chat(last_cmd: str) -> str:
    """Return the initial message when chat starts."""
    return f"There seems to be a problem with '{last_cmd}'. Let's sort it out."


def chat(message: str) -> str:
    """Very small echo-style chat."""
    return f"Johny: {message}"
