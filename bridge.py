import asyncio
import os
import time
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import uvicorn

PROMPT = ">>"


class LetsGoProcess:
    """Manage a persistent letsgo.py subprocess."""

    def __init__(self) -> None:
        self.proc: asyncio.subprocess.Process | None = None

    async def start(self) -> None:
        self.proc = await asyncio.create_subprocess_exec(
            "python",
            "letsgo.py",
            "--no-color",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )
        await self._read_until_prompt()

    async def _read_until_prompt(self) -> None:
        if not self.proc:
            return
        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break
            if line.decode().strip() == PROMPT:
                break

    async def run(self, cmd: str) -> str:
        if not self.proc:
            raise RuntimeError("process not started")
        assert self.proc.stdin
        self.proc.stdin.write((cmd + "\n").encode())
        await self.proc.stdin.drain()
        lines: list[str] = []
        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break
            text = line.decode()
            if text.strip() == PROMPT:
                break
            if text.startswith(PROMPT + " "):
                text = text[len(PROMPT) + 1 :]
            lines.append(text)
        return "".join(lines).strip()


letsgo = LetsGoProcess()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBasic()
API_TOKEN = os.getenv("API_TOKEN", "change-me")
RATE_LIMIT = float(os.getenv("RATE_LIMIT_SEC", "1"))
_last_call: Dict[str, float] = {}


def _check_rate(client: str) -> None:
    now = time.time()
    if now - _last_call.get(client, 0) < RATE_LIMIT:
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    _last_call[client] = now


@app.post("/run")
async def run_command(
    cmd: str, credentials: HTTPBasicCredentials = Depends(security)
) -> Dict[str, str]:
    if credentials.password != API_TOKEN:
        raise HTTPException(status_code=401, detail="unauthorized")
    _check_rate(credentials.username)
    output = await letsgo.run(cmd)
    return {"output": output}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if token != API_TOKEN:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    try:
        while True:
            cmd = await websocket.receive_text()
            output = await letsgo.run(cmd)
            await websocket.send_text(output)
    except WebSocketDisconnect:
        pass


async def handle_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cmd = update.message.text if update.message else ""
    if not cmd:
        return
    output = await letsgo.run(cmd)
    await update.message.reply_text(output)


async def start_bot() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        return
    application = ApplicationBuilder().token(token).build()
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram)
    )
    await application.run_polling()


async def main() -> None:
    await letsgo.start()
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
    )
    await asyncio.gather(server.serve(), start_bot())


if __name__ == "__main__":
    asyncio.run(main())
