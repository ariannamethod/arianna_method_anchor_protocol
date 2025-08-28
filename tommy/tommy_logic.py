"""Utility functions for Tommy's logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import sqlite3

from . import tommy as _tommy
from arianna_utils.vector_store import SQLiteVectorStore, embed_text

# Global vector store located alongside other Tommy databases
_VECTOR_STORE = SQLiteVectorStore(_tommy.LOG_DIR / "vectors.db")


def fetch_context(ts: str, radius: int = 10) -> list[tuple[str, str, str]]:
    """Return events surrounding a timestamp.

    Parameters
    ----------
    ts:
        Timestamp string to search for.
    radius:
        Number of events to include before and after the timestamp.

    Returns
    -------
    list[tuple[str, str, str]]
        Ordered list of ``(ts, type, message)`` tuples. Returns an empty list
        if the timestamp is not found.
    """
    with sqlite3.connect(_tommy.DB_PATH, timeout=30) as conn:
        cur = conn.execute("SELECT rowid FROM events WHERE ts = ?", (ts,))
        row = cur.fetchone()
        if not row:
            return []
        rowid = row[0]
        start = max(rowid - radius, 1)
        end = rowid + radius
        cur = conn.execute(
            "SELECT ts, type, message FROM events "
            "WHERE rowid BETWEEN ? AND ? ORDER BY rowid",
            (start, end),
        )
        return cur.fetchall()


def search_context(query: str, top_k: int = 5) -> list[str]:
    """Return stored messages most similar to ``query``.

    Parameters
    ----------
    query:
        Free text to embed and compare against stored memories.
    top_k:
        Maximum number of results to return.
    """
    embedding = embed_text(query)
    hits = _VECTOR_STORE.query_similar(embedding, top_k)
    return [h.content for h in hits]


@dataclass
class Snapshot:
    """Representation of a daily snapshot."""

    date: datetime
    summary: str
    prediction: str | None = None
    evaluation: str | None = None


def _ensure_snapshot_table(conn: sqlite3.Connection) -> None:
    """Ensure the ``snapshots`` table exists."""

    conn.execute(
        "CREATE TABLE IF NOT EXISTS snapshots ("
        "date TEXT PRIMARY KEY, "
        "summary TEXT, "
        "prediction TEXT, "
        "evaluation TEXT)"
    )


def create_daily_snapshot(date: datetime) -> Snapshot:
    """Aggregate events for a given day into a snapshot.

    Parameters
    ----------
    date:
        Day for which to aggregate events.
    """

    start = datetime(date.year, date.month, date.day)
    end = start + timedelta(days=1)
    with sqlite3.connect(_tommy.DB_PATH, timeout=30) as conn:
        _ensure_snapshot_table(conn)
        cur = conn.execute(
            "SELECT message FROM events WHERE ts >= ? AND ts < ? ORDER BY ts",
            (start.isoformat(), end.isoformat()),
        )
        messages = [row[0] for row in cur.fetchall()]
        summary = " | ".join(messages)
        cur = conn.execute(
            "SELECT prediction, evaluation FROM snapshots WHERE date = ?",
            (start.date().isoformat(),),
        )
        row = cur.fetchone()
        prediction = row[0] if row else ""
        evaluation = row[1] if row else ""
        conn.execute(
            "INSERT OR REPLACE INTO snapshots (date, summary, prediction, evaluation)"
            " VALUES (?, ?, ?, ?)",
            (start.date().isoformat(), summary, prediction, evaluation),
        )

    # Index snapshot summary and individual messages for similarity search
    for msg in messages:
        _VECTOR_STORE.add_memory("event", msg, embed_text(msg))
    if summary:
        _VECTOR_STORE.add_memory("snapshot", summary, embed_text(summary))

    return Snapshot(start, summary, prediction or None, evaluation or None)


def compare_with_previous(
    snapshot_today: Snapshot, snapshot_yesterday: Snapshot
) -> str:
    """Compare two snapshots and evaluate yesterday's prediction."""

    today_count = (
        len(snapshot_today.summary.split(" | ")) if snapshot_today.summary else 0
    )
    match = re.search(r"\d+", snapshot_yesterday.prediction or "")
    expected = int(match.group(0)) if match else None
    if expected is None:
        evaluation = "no prediction"
    else:
        evaluation = f"predicted {expected}, got {today_count}"
    with sqlite3.connect(_tommy.DB_PATH, timeout=30) as conn:
        _ensure_snapshot_table(conn)
        conn.execute(
            "UPDATE snapshots SET evaluation = ? WHERE date = ?",
            (evaluation, snapshot_yesterday.date.strftime("%Y-%m-%d")),
        )
    return evaluation


def predict_tomorrow(snapshot_today: Snapshot) -> str:
    """Generate a simple forecast for the next day."""

    count = len(snapshot_today.summary.split(" | ")) if snapshot_today.summary else 0
    prediction = f"{count} events tomorrow"
    with sqlite3.connect(_tommy.DB_PATH, timeout=30) as conn:
        _ensure_snapshot_table(conn)
        conn.execute(
            "UPDATE snapshots SET prediction = ? WHERE date = ?",
            (prediction, snapshot_today.date.strftime("%Y-%m-%d")),
        )
    return prediction


def analyze_resonance(window: int) -> str:
    """Analyze resonance history over the given window in days.

    Parameters
    ----------
    window:
        Number of days to look back for resonance events.

    Returns
    -------
    str
        Short textual report summarizing sentiment trend and anomalies.
    """

    cutoff = datetime.now() - timedelta(days=window)
    with sqlite3.connect(_tommy.RESONANCE_DB_PATH, timeout=30) as conn:
        cur = conn.execute(
            "SELECT ts, sentiment FROM resonance WHERE ts >= ? ORDER BY ts",
            (cutoff.isoformat(),),
        )
        rows = cur.fetchall()
    if not rows:
        return "No resonance data."
    total = len(rows)
    pos = sum(1 for _, s in rows if s == "positive")
    neg = sum(1 for _, s in rows if s == "negative")
    neu = total - pos - neg
    trend = "positive" if pos >= neg else "negative"
    anomaly = "Anomaly detected" if neg > pos * 2 else "Stable"
    return (
        f"{total} entries in last {window} days: "
        f"{pos} positive, {neg} negative, {neu} neutral. "
        f"Trend {trend}. {anomaly}."
    )
