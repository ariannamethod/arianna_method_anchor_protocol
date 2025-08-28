import asyncio

import pytest

try:  # pragma: no cover - optional dependency
    from bridge import LetsGoProcess, _get_user_proc, user_sessions
except ModuleNotFoundError:  # fastapi missing
    pytest.skip("fastapi not installed", allow_module_level=True)


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


def test_get_user_proc_restarts_stopped_process(monkeypatch):
    user_id = 42
    started = False

    async def fake_start(self):
        nonlocal started
        started = True
        self.proc = _DummyProcess()

    proc = LetsGoProcess()
    proc.proc = None
    user_sessions[user_id] = proc
    monkeypatch.setattr(LetsGoProcess, "start", fake_start)

    try:
        result = asyncio.run(_get_user_proc(user_id))
        assert started
        assert result.proc is not None
    finally:
        user_sessions.pop(user_id, None)
