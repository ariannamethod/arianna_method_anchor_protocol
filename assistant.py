#!/usr/bin/env python3
"""Interactive console assistant for Arianna Core."""

from __future__ import annotations

import os
import socket
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Deque

# //: each session logs to its own file
LOG_DIR = Path(__file__).resolve().parent / "log"
SESSION_ID = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
LOG_PATH = LOG_DIR / f"{SESSION_ID}.log"


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} {message}\n")


def _first_ip() -> str:
    """Return the first non-loopback IP address or 'unknown'."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        try:
            for addr in socket.gethostbyname_ex(socket.gethostname())[2]:
                if not addr.startswith("127."):
                    return addr
        except socket.gaierror:
            pass
    return "unknown"


def status() -> str:
    """Return basic system metrics."""
    cpu = os.cpu_count()
    uptime = Path("/proc/uptime").read_text().split()[0]
    ip = _first_ip()
    return f"CPU cores: {cpu}\nUptime: {uptime}s\nIP: {ip}"


def summarize(term: str | None = None, limit: int = 5) -> str:
    """Naive log search returning last ``limit`` matches."""
    if not LOG_DIR.exists():
        return "no logs"
    lines: Deque[str] = deque(maxlen=limit)
    for file in sorted(LOG_DIR.glob("*.log")):
        with file.open() as fh:
            for line in fh:
                line = line.rstrip("\n")
                if term is None or term in line:
                    lines.append(line)
    return "\n".join(lines) if lines else "no matches"


def main() -> None:
    log("session_start")
    print("Arianna assistant ready. Type 'exit' to quit.")
    while True:
        try:
            user = input(">> ")
        except EOFError:
            break
        if user.strip().lower() in {"exit", "quit"}:
            break
        log(f"user:{user}")
        if user.strip() == "/status":
            reply = status()
        elif user.startswith("/summarize"):
            parts = user.split()[1:]
            limit = 5
            if parts and parts[-1].isdigit():
                limit = int(parts[-1])
                parts = parts[:-1]
            term = " ".join(parts) if parts else None
            reply = summarize(term, limit)
        else:
            reply = f"echo: {user}"
        print(reply)
        log(f"assistant:{reply}")
    log("session_end")


if __name__ == "__main__":
    main()
