import os
import sqlite3
import time
from datetime import datetime, timedelta

from tommy import tommy


def setup_env(monkeypatch, tmp_path):
    monkeypatch.setattr(tommy, "LOG_DIR", tmp_path)
    monkeypatch.setattr(tommy, "DB_PATH", tmp_path / "tommy.sqlite3")
    monkeypatch.setattr(tommy, "RESONANCE_DB_PATH", tmp_path / "resonance.sqlite3")
    tommy._init_db()
    tommy._init_resonance_db()


def test_event_pruning(monkeypatch, tmp_path):
    setup_env(monkeypatch, tmp_path)
    monkeypatch.setattr(tommy, "EVENT_RETENTION_DAYS", 1)
    old_ts = (datetime.now() - timedelta(days=2)).isoformat()
    with sqlite3.connect(tommy.DB_PATH) as conn:
        conn.execute(
            "INSERT INTO events (ts, type, message) VALUES (?, ?, ?)",
            (old_ts, "info", "old"),
        )
    tommy.log_event("new")
    with sqlite3.connect(tommy.DB_PATH) as conn:
        rows = conn.execute("SELECT message FROM events").fetchall()
    assert [r[0] for r in rows] == ["new"]


def test_resonance_pruning(monkeypatch, tmp_path):
    setup_env(monkeypatch, tmp_path)
    monkeypatch.setattr(tommy, "RESONANCE_RETENTION_DAYS", 1)
    old_ts = (datetime.now() - timedelta(days=2)).isoformat()
    with sqlite3.connect(tommy.RESONANCE_DB_PATH) as conn:
        conn.execute(
            "INSERT INTO resonance (ts, agent, role, sentiment, snapshots, summary) VALUES (?, ?, ?, ?, ?, ?)",
            (old_ts, "test", "r", "s", "", "old"),
        )
    tommy.update_resonance()
    with sqlite3.connect(tommy.RESONANCE_DB_PATH) as conn:
        rows = conn.execute("SELECT summary FROM resonance").fetchall()
    assert [r[0] for r in rows][-1] != "old"


def test_log_rotation_and_cleanup(monkeypatch, tmp_path):
    setup_env(monkeypatch, tmp_path)
    monkeypatch.setattr(tommy, "MAX_LOG_SIZE", 100)
    monkeypatch.setattr(tommy, "LOG_RETENTION_DAYS", 0)
    # create oversized current log
    log_file = tmp_path / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    log_file.write_text("x" * 150)
    # create old log
    old_log = tmp_path / "old.jsonl"
    old_log.write_text("old")
    old_mtime = time.time() - 86400 * 2
    os.utime(old_log, (old_mtime, old_mtime))

    tommy.log_event("entry")

    rotated = list(tmp_path.glob(f"{datetime.now().strftime('%Y-%m-%d')}_*.jsonl"))
    assert rotated, "rotation did not occur"
    assert not old_log.exists()
