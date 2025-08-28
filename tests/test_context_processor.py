import asyncio
from pathlib import Path

from arianna_utils import context_neural_processor as cnp
from arianna_utils.vector_store import SQLiteVectorStore, embed_text


class _DummyESN:
    def update(self, text: str, pulse: float) -> None:  # pragma: no cover - trivial
        pass


def test_parse_and_store_file(tmp_path, monkeypatch):
    # Redirect cache database to temporary directory and reset
    monkeypatch.setattr(cnp, "CACHE_DB", tmp_path / "cache.db")
    cnp.init_cache_db()

    # Avoid numpy dependency during tests
    monkeypatch.setattr(cnp, "esn", _DummyESN())

    sample = tmp_path / "sample.txt"
    sample.write_text("hello world")

    engine = SQLiteVectorStore(tmp_path / "vectors.db")
    result = asyncio.run(cnp.parse_and_store_file(str(sample), engine=engine))

    assert "hello world" in result
    hits = engine.query_similar(embed_text("hello world"), top_k=1)
    assert hits and "hello world" in hits[0].content
