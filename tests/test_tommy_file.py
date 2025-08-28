import asyncio
import sqlite3
from pathlib import Path

from tommy.tommy_logic import process_file_with_context
from tommy import tommy as t
from arianna_utils import context_neural_processor as cnp
from arianna_utils.vector_store import SQLiteVectorStore


class _DummyESN:
    def update(self, text: str, pulse: float) -> None:  # pragma: no cover - trivial
        pass


def test_process_file_with_context_logs(tmp_path, monkeypatch):
    # Redirect Tommy's databases to temporary locations
    log_dir = tmp_path / "log"
    log_dir.mkdir()
    monkeypatch.setattr(t, "LOG_DIR", log_dir)
    monkeypatch.setattr(t, "DB_PATH", log_dir / "tommy.sqlite3")
    monkeypatch.setattr(t, "RESONANCE_DB_PATH", log_dir / "resonance.sqlite3")
    t._init_db()
    t._init_resonance_db()

    # Prepare context processor cache and dependencies
    monkeypatch.setattr(cnp, "CACHE_DB", tmp_path / "cache.db")
    cnp.init_cache_db()
    monkeypatch.setattr(cnp, "esn", _DummyESN())

    sample = tmp_path / "sample.txt"
    sample.write_text("hello world")

    engine = SQLiteVectorStore(tmp_path / "vectors.db")
    result = asyncio.run(process_file_with_context(str(sample), engine=engine))

    assert "hello world" in result

    with sqlite3.connect(t.DB_PATH, timeout=30) as conn:
        rows = conn.execute("SELECT message FROM events").fetchall()
    assert any("Processed" in r[0] for r in rows)
