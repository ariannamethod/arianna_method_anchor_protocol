from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sqlite3


def prune_old_records(
    conn: sqlite3.Connection, table: str, retention_days: int
) -> None:
    """Delete records older than ``retention_days`` from ``table``.

    Parameters
    ----------
    conn:
        Open SQLite connection.
    table:
        Name of the table with a ``ts`` column.
    retention_days:
        Number of days to keep.
    """
    cutoff = datetime.now() - timedelta(days=retention_days)
    conn.execute(f"DELETE FROM {table} WHERE ts < ?", (cutoff.isoformat(),))


def prepare_log_file(
    log_dir: Path,
    prefix: str = "",
    max_size: int = 5 * 1024 * 1024,
    retention_days: int = 7,
) -> Path:
    """Return path for current log file, rotating and cleaning up old files.

    Files are named ``{prefix}%Y-%m-%d.jsonl``. If the current file exceeds
    ``max_size`` bytes it is rotated with an incremental suffix. Files older
    than ``retention_days`` are removed.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_name = f"{prefix}{date_str}.jsonl"
    log_file = log_dir / base_name

    if log_file.exists() and log_file.stat().st_size > max_size:
        idx = 1
        while (log_dir / f"{prefix}{date_str}_{idx}.jsonl").exists():
            idx += 1
        log_file.rename(log_dir / f"{prefix}{date_str}_{idx}.jsonl")
        log_file = log_dir / base_name

    cutoff = datetime.now() - timedelta(days=retention_days)
    for old in log_dir.glob(f"{prefix}*.jsonl"):
        mtime = datetime.fromtimestamp(old.stat().st_mtime)
        if mtime < cutoff:
            try:
                old.unlink()
            except FileNotFoundError:
                pass

    return log_file
