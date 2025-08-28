import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tommy import tommy


def test_resonance_records_last_five(monkeypatch, tmp_path):
    monkeypatch.setattr(tommy, "LOG_DIR", tmp_path)
    monkeypatch.setattr(tommy, "DB_PATH", tmp_path / "tommy.sqlite3")
    monkeypatch.setattr(tommy, "RESONANCE_DB_PATH", tmp_path / "resonance.sqlite3")
    tommy._init_db()
    tommy._init_resonance_db()
    for i in range(7):
        tommy.log_event(f"user:msg{i}")
    tommy.update_resonance()
    conn = sqlite3.connect(tommy.RESONANCE_DB_PATH)
    cur = conn.execute("SELECT summary FROM resonance ORDER BY rowid DESC LIMIT 1")
    summary = cur.fetchone()[0]
    conn.close()
    assert "msg2" in summary and "msg6" in summary
    assert "msg1" not in summary
