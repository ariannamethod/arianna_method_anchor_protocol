import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tommy  # noqa: E402


def test_xplaine_ignores_xplaineoff(monkeypatch, tmp_path):
    monkeypatch.setattr(tommy, "LOG_DIR", tmp_path)
    monkeypatch.setattr(tommy, "DB_PATH", tmp_path / "tommy.sqlite3")
    tommy._init_db()
    tommy.log_event("user:ls")
    tommy.log_event("user:/xplaineoff")
    tommy.log_event("user:/xplaine")
    captured = {}

    async def fake_query(prompt):
        captured["prompt"] = prompt
        return "advice"

    monkeypatch.setattr(tommy, "query_grok3", fake_query)
    result = asyncio.run(tommy.xplaine())
    assert result == "advice"
    assert "ls" in captured["prompt"]
    assert "previous command was: /xplaineoff" not in captured["prompt"]
