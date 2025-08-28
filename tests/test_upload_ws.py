import importlib
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import bridge


def test_upload_ws_respects_max_size(tmp_path, monkeypatch):
    monkeypatch.setenv("API_TOKEN", "secret")
    monkeypatch.setenv("MAX_UPLOAD_SIZE", "5")
    importlib.reload(bridge)
    bridge.UPLOAD_DIR = str(tmp_path)
    client = TestClient(bridge.app)
    with client.websocket_connect("/upload?token=secret&name=data.bin") as ws:
        ws.send_bytes(b"abcdef")
        with pytest.raises(WebSocketDisconnect):
            ws.receive_bytes()
    assert not (tmp_path / "data.bin").exists()
