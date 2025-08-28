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


def test_paraphrase_uses_full_text(monkeypatch):
    class DummyGen:
        def generate(self, prefix, n, temp):
            return prefix

    monkeypatch.setattr(cnp, "cg", DummyGen())
    long_text = "A" * 210 + "END"
    result = asyncio.run(cnp.paraphrase(long_text, prefix=""))
    assert "END" in result


def test_parse_and_store_file_uses_full_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(cnp, "CACHE_DB", tmp_path / "cache.db")
    cnp.init_cache_db()
    monkeypatch.setattr(cnp, "esn", _DummyESN())

    long_text = "A" * 210 + "END"
    sample = tmp_path / "sample.txt"
    sample.write_text(long_text)

    async def fake_paraphrase(text, prefix="Summarize this for kids: "):
        return text

    monkeypatch.setattr(cnp, "paraphrase", fake_paraphrase)
    engine = SQLiteVectorStore(tmp_path / "vectors.db")
    result = asyncio.run(cnp.parse_and_store_file(str(sample), engine=engine))

    summary_line = result.split("Summary: ")[1].split("\nRelevance")[0]
    assert "END" in summary_line
