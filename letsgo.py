#!/usr/bin/env python3
"""Interactive console terminal for Arianna Core."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import readline
import atexit
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Deque, Iterable, List

# ANSI color codes
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[36m"
RESET = "\033[0m"

_NO_COLOR_FLAG = "--no-color"
USE_COLOR = (
    os.getenv("LETSGO_NO_COLOR") is None
    and os.getenv("NO_COLOR") is None
    and _NO_COLOR_FLAG not in sys.argv
)
if _NO_COLOR_FLAG in sys.argv:
    sys.argv.remove(_NO_COLOR_FLAG)


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if USE_COLOR else text

# //: each session logs to its own file under a fixed directory
LOG_DIR = Path("/arianna_core/log")
SESSION_ID = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
LOG_PATH = LOG_DIR / f"{SESSION_ID}.log"
HISTORY_PATH = LOG_DIR / "history"

COMMANDS: List[str] = [
    "/status",
    "/time",
    "/run",
    "/summarize",
    "/help",
]


def _ensure_log_dir() -> None:
    """Ensure that the log directory exists and is writable."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not os.access(LOG_DIR, os.W_OK):
        print(f"No write permission for {LOG_DIR}", file=sys.stderr)
        raise SystemExit(1)


def log(message: str) -> None:
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


def current_time() -> str:
    """Return the current UTC time."""
    return datetime.utcnow().isoformat()


def run_command(command: str) -> str:
    """Execute a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        output = exc.stdout.strip() if exc.stdout else str(exc)
        return color(output, RED)


def _iter_log_lines() -> Iterable[str]:
    """Yield log lines from all log files in order."""
    for file in sorted(LOG_DIR.glob("*.log")):
        with file.open() as fh:
            for line in fh:
                yield line.rstrip("\n")


def summarize(term: str | None = None, limit: int = 5) -> str:
    """Return the last ``limit`` log lines matching ``term``."""
    if not LOG_DIR.exists():
        return "no logs"
    matches: Deque[str] = deque(maxlen=limit)
    for line in _iter_log_lines():
        if term is None or term in line:
            matches.append(line)
    return "\n".join(matches) if matches else "no matches"


def main() -> None:
    _ensure_log_dir()
    try:
        readline.read_history_file(str(HISTORY_PATH))
    except FileNotFoundError:
        pass
    readline.parse_and_bind("tab: complete")

    def completer(text: str, state: int) -> str | None:
        matches = [cmd for cmd in COMMANDS if cmd.startswith(text)]
        return matches[state] if state < len(matches) else None

    readline.set_completer(completer)
    atexit.register(readline.write_history_file, str(HISTORY_PATH))

    log("session_start")
    print("LetsGo terminal ready. Type 'exit' to quit.")
    while True:
        try:
            user = input(color(">> ", CYAN))
        except EOFError:
            break
        if user.strip().lower() in {"exit", "quit"}:
            break
        log(f"user:{user}")
        if user.strip() == "/status":
            reply = status()
            colored = color(reply, GREEN)
        elif user.strip() == "/time":
            reply = current_time()
            colored = reply
        elif user.startswith("/run "):
            reply = run_command(user.partition(" ")[2])
            colored = reply
        elif user.strip() == "/help":
            reply = (
                "Commands: /status, /time, /run <cmd>, "
                "/summarize [term [limit]]"
            )
            colored = reply
        elif user.startswith("/summarize"):
            parts = user.split()[1:]
            limit = 5
            if parts and parts[-1].isdigit():
                limit = int(parts[-1])
                parts = parts[:-1]
            term = " ".join(parts) if parts else None
            reply = summarize(term, limit)
            colored = reply
        else:
            reply = f"echo: {user}"
            colored = reply
        print(colored)
        log(f"letsgo:{reply}")
    log("session_end")


if __name__ == "__main__":
    main()
