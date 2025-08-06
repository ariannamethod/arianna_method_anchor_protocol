#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import shutil  # //: filesystem operations available for future expansion

LOG_PATH = Path(__file__).resolve().parents[1] / "log" / "session.log"


def log(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a") as fh:
        fh.write(f"{datetime.utcnow().isoformat()} {message}\n")


def main() -> None:
    print("Arianna assistant ready. Type 'exit' to quit.")
    while True:
        try:
            user = input(">> ")
        except EOFError:
            break
        if user.strip().lower() in {"exit", "quit"}:
            break
        log(f"user:{user}")
        reply = f"echo: {user}"
        print(reply)  # //: placeholder AI response, will expand
        log(f"assistant:{reply}")
    log("session end")


if __name__ == "__main__":
    main()
