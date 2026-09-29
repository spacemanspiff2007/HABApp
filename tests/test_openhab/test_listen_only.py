from unittest.mock import Mock

import pytest

from HABApp.config.models.openhab import General as OhGeneral
from HABApp.config.models.openhab import OpenhabConfig
from HABApp.core.lib import WatchedSingleConsumerQueue
from HABApp.openhab.connection.handler import OhClientSession
from HABApp.openhab.connection.handler import _connection as connection_module
from HABApp.openhab.connection.plugins import OutgoingCommandsPlugin, WebsocketPlugin


async def test_listen_only_ws() -> None:
    cfg = OpenhabConfig(general=OhGeneral(listen_only=True))
    queue = WatchedSingleConsumerQueue()

    plugin = WebsocketPlugin(
        event_handler=Mock(), asyncio_provider=Mock(), ws_queue=queue, session=Mock(), config=cfg
    )

    plugin.cfg_updated()
    assert not queue.is_open

    cfg.general.listen_only = False
    plugin.cfg_updated()
    assert queue.is_open


async def test_listen_only_out() -> None:
    cfg = OhGeneral(listen_only=True)
    queue = WatchedSingleConsumerQueue()

    plugin = OutgoingCommandsPlugin(
        asyncio_provider=Mock(), http_queue=queue, oh_connection=Mock(), config=cfg
    )

    plugin.cfg_updated()
    assert not queue.is_open

    cfg.listen_only = False
    plugin.cfg_updated()
    assert queue.is_open


async def test_listen_only_session(monkeypatch) -> None:

    def err(*args, **kwargs):
        msg = 'REQUEST_WAS_MADE'
        raise ValueError(msg)

    monkeypatch.setattr(connection_module, '_RequestContextManager', Mock(side_effect=err))

    cfg = OhGeneral(listen_only=True)

    connection = OhClientSession(Mock(), Mock(), ssl=False)
    connection.update_cfg(cfg)
    assert await connection.post('asdf') is None

    cfg.listen_only = False
    connection.update_cfg(cfg)

    with pytest.raises(ValueError, match=r'^REQUEST_WAS_MADE$'):
        await connection.post('asdf')
