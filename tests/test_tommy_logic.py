import sqlite3

import tommy.tommy as tommy
from tommy.tommy_logic import fetch_context


def test_fetch_context(tmp_path, monkeypatch):
    db_path = tmp_path / "tommy.sqlite3"
    monkeypatch.setattr(tommy, "DB_PATH", db_path)
    tommy._init_db()
    records = [
        (f"2024-01-01T00:00:0{i}", "info", f"msg{i}") for i in range(5)
    ]
    with sqlite3.connect(db_path, timeout=30) as conn:
        conn.executemany(
            "INSERT INTO events (ts, type, message) VALUES (?, ?, ?)",
            records,
        )
    target_ts = records[2][0]
    ctx = fetch_context(target_ts, radius=1)
    messages = [m for _, _, m in ctx]
    assert messages == ["msg1", "msg2", "msg3"]
    assert fetch_context("nope") == []

