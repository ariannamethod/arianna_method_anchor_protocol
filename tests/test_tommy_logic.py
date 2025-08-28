import sqlite3
from datetime import datetime

from tommy import tommy_logic as tl
from tommy import tommy as tommy_mod


def test_snapshot_vector_integration(tmp_path, monkeypatch):
    db_path = tmp_path / "events.db"
    monkeypatch.setattr(tommy_mod, "DB_PATH", db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE events (ts TEXT, type TEXT, message TEXT)")
        ts = datetime.now().replace(microsecond=0).isoformat()
        conn.execute(
            "INSERT INTO events (ts, type, message) VALUES (?, ?, ?)",
            (ts, "info", "alpha event"),
        )

    store = tl.SQLiteVectorStore(tmp_path / "vectors.db")
    monkeypatch.setattr(tl, "_VECTOR_STORE", store)

    tl.create_daily_snapshot(datetime.now())
    results = tl.search_context("alpha")
    assert results and "alpha" in results[0]
