from dataclasses import dataclass
from typing import Dict, List
from unittest.mock import Mock

import pytest

from HABApp.openhab.connection_handler import http_connection
from HABApp.openhab.connection_logic.plugin_load_items import LoadAllOpenhabItems


class FalseFuture:
    @staticmethod
    def done():
        return True


@dataclass
class SimpleReqInfo:
    method: str
    url: str


class DummyResp:
    def __init__(self, url: str, status: int, json=None):
        self.url = url
        self.status = status
        self._json = json
        self.request_info = None

    async def json(self, *args, **kwargs):
        return self._json


RESPONSES: Dict[str, List[DummyResp]] = {}


class MySession:
    _PREFIX = '/rest/'

    @staticmethod
    async def _request(meth: str, url: str, **kwargs):
        assert meth == 'GET'
        if url.startswith(MySession._PREFIX):
            url = url[len(MySession._PREFIX):]

        return RESPONSES[url].pop(0)

    @staticmethod
    def add_resp(obj: DummyResp):
        http_connection.IS_ONLINE = True
        obj.request_info = SimpleReqInfo('GET', MySession._PREFIX + obj.url)
        RESPONSES.setdefault(obj.url, []).append(obj)


@pytest.mark.asyncio
async def test_disconnect(monkeypatch, caplog):
    disconnect_cb = Mock()

    # Disable automatic reconnect
    monkeypatch.setattr(http_connection, 'try_uuid', lambda: 1)
    monkeypatch.setattr(http_connection, 'FUT_UUID', FalseFuture)
    monkeypatch.setattr(http_connection, 'IS_NOT_SET_UP', False)
    monkeypatch.setattr(http_connection.asyncio, 'run_coroutine_threadsafe', lambda x, y: FalseFuture)

    # Use dummy session
    monkeypatch.setattr(http_connection, 'ON_DISCONNECTED', disconnect_cb)
    monkeypatch.setattr(http_connection, 'HTTP_SESSION', MySession)

    # 404 on item request
    disconnect_cb.assert_not_called()

    MySession.add_resp(DummyResp('items', 404))
    p = LoadAllOpenhabItems()
    await p.on_connect_function()

    disconnect_cb.assert_called_once()
    disconnect_cb.reset_mock()

    # 404 on thing request
    disconnect_cb.assert_not_called()

    MySession.add_resp(DummyResp('items', 200, json=[]))
    MySession.add_resp(DummyResp('things', 404))
    p = LoadAllOpenhabItems()
    await p.on_connect_function()

    disconnect_cb.assert_called_once()
    disconnect_cb.reset_mock()

    # everything works
    disconnect_cb.assert_not_called()

    MySession.add_resp(DummyResp('items', 200, json=[]))
    MySession.add_resp(DummyResp('things', 200, json=[]))
    p = LoadAllOpenhabItems()
    await p.on_connect_function()

    disconnect_cb.assert_not_called()
