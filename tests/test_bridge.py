import asyncio

from bridge import LetsGoProcess


class _DummyStdin:
    def close(self) -> None:  # pragma: no cover
        pass


class _DummyProcess:
    def __init__(self) -> None:
        self.stdin = _DummyStdin()

    def terminate(self) -> None:
        raise ProcessLookupError

    async def wait(self) -> None:
        raise ProcessLookupError


def test_stop_handles_missing_process():
    proc = LetsGoProcess()
    proc.proc = _DummyProcess()
    asyncio.run(proc.stop())
    assert proc.proc is None
