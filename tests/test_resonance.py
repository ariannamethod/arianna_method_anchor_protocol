import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tommy import tommy
from tommy.tommy_logic import analyze_resonance


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
    cur = conn.execute(
        "SELECT summary, role, sentiment, snapshots FROM resonance ORDER BY rowid DESC LIMIT 1"
    )
    summary, role, sentiment, snaps = cur.fetchone()
    conn.close()
    assert "msg2" in summary and "msg6" in summary
    assert "msg1" not in summary
    assert role == "guardian"
    assert sentiment in {"neutral", "positive", "negative"}
    assert isinstance(snaps, str)


def test_analyze_resonance(monkeypatch, tmp_path):
    monkeypatch.setattr(tommy, "LOG_DIR", tmp_path)
    monkeypatch.setattr(tommy, "DB_PATH", tmp_path / "tommy.sqlite3")
    monkeypatch.setattr(tommy, "RESONANCE_DB_PATH", tmp_path / "resonance.sqlite3")
    tommy._init_db()
    tommy._init_resonance_db()
    tommy.log_event("user:all good")
    tommy.update_resonance()
    tommy.log_event("user:error happened")
    tommy.update_resonance()
    report = analyze_resonance(1)
    assert "2 entries" in report
