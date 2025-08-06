from typing import Tuple


async def _ping(_: str) -> Tuple[str, str | None]:
    reply = "pong"
    return reply, reply


def register(commands, handlers):
    commands.append("/ping")
    handlers["/ping"] = _ping
