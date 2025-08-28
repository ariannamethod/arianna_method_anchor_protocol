"""Utility functions for Tommy's logic."""
from __future__ import annotations

import sqlite3

from . import tommy as _tommy


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
