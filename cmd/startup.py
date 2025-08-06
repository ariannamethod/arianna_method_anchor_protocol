#!/usr/bin/env python3
"""Launch assistant on login."""
import subprocess
from pathlib import Path

ASSISTANT = Path(__file__).resolve().parents[1] / "assistant.py"


def main() -> None:
    subprocess.run(["python3", str(ASSISTANT)])


if __name__ == "__main__":
    main()
