import sqlite3
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tommy import tommy
from tommy.tommy_logic import (
    compare_with_previous,
    create_daily_snapshot,
    predict_tomorrow,
)


def setup_env(monkeypatch, tmp_path):
    monkeypatch.setattr(tommy, "LOG_DIR", tmp_path)
    monkeypatch.setattr(tommy, "DB_PATH", tmp_path / "tommy.sqlite3")
    monkeypatch.setattr(tommy, "RESONANCE_DB_PATH", tmp_path / "resonance.sqlite3")
    tommy._init_db()
    tommy._init_resonance_db()


def test_snapshot_flow(monkeypatch, tmp_path):
    setup_env(monkeypatch, tmp_path)
    with sqlite3.connect(tommy.DB_PATH, timeout=30) as conn:
        conn.execute(
            "INSERT INTO events (ts, type, message) VALUES (?, ?, ?)",
            ("2024-05-01T10:00:00", "info", "day1"),
        )
        conn.execute(
            "INSERT INTO events (ts, type, message) VALUES (?, ?, ?)",
            ("2024-05-02T09:00:00", "info", "day2"),
        )
    snap1 = create_daily_snapshot(datetime(2024, 5, 1))
    snap1.prediction = predict_tomorrow(snap1)
    snap2 = create_daily_snapshot(datetime(2024, 5, 2))
    evaluation = compare_with_previous(snap2, snap1)
    assert "predicted" in evaluation
    tommy.update_resonance()
    with sqlite3.connect(tommy.RESONANCE_DB_PATH, timeout=30) as conn:
        cur = conn.execute(
            "SELECT summary FROM resonance ORDER BY rowid DESC LIMIT 1"
        )
        summary = cur.fetchone()[0]
    assert "predicted" in summary
