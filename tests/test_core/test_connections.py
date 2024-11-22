from unittest.mock import Mock

import pytest

from HABApp.core.connections import BaseConnection, BaseConnectionPlugin, PluginCallbackHandler
from HABApp.core.connections.status_transitions import ConnectionStatus, StatusTransitions


def test_transitions() -> None:
    status = StatusTransitions()

    def get_flow() -> list[str]:
        ret = []
        while add := status.advance_status():
            ret.append(add.value)
        return ret

    status.setup = True
    assert get_flow() == ['SETUP', 'CONNECTING', 'CONNECTED', 'ONLINE']

    # No error
    for initial_state in (ConnectionStatus.CONNECTING, ConnectionStatus.CONNECTED, ConnectionStatus.ONLINE):
        status = StatusTransitions()
        status.status = initial_state
        status.setup = True

        assert get_flow() == ['DISCONNECTED', 'OFFLINE', 'SETUP', 'CONNECTING', 'CONNECTED', 'ONLINE']

    # Error Handling
    for initial_state in (ConnectionStatus.CONNECTING, ConnectionStatus.CONNECTED, ConnectionStatus.ONLINE):
        status = StatusTransitions()
        status.status = initial_state
        status.error = True

        assert get_flow() == ['DISCONNECTED', 'OFFLINE']

    # Shutdown
    for initial_state in (ConnectionStatus.CONNECTING, ConnectionStatus.CONNECTED, ConnectionStatus.ONLINE):
        status = StatusTransitions()
        status.status = initial_state
        status.shutdown = True

        assert get_flow() == ['DISCONNECTED', 'OFFLINE', 'SHUTDOWN']


async def test_plugin_callback() -> None:

    sentinel = object()
    mock_connected = Mock()
    mock_setup = Mock()

    class TestPlugin(BaseConnectionPlugin):
        def __init__(self) -> None:
            super().__init__('asdf')

        async def on_connected(self, context) -> None:
            assert context is sentinel
            mock_connected()

        async def on_disconnected(self) -> None:
            pass

        async def on_setup(self, context, connection) -> None:
            assert context is sentinel
            assert connection is b
            mock_setup()

    b = BaseConnection('test')
    b.register_plugin(TestPlugin())

    b.context = sentinel
    mock_connected.assert_not_called()
    mock_setup.assert_not_called()

    b.status.status = ConnectionStatus.CONNECTED
    b.plugin_task.start()
    await b.plugin_task.wait()

    mock_connected.assert_called_once()
    mock_setup.assert_not_called()

    b.status.status = ConnectionStatus.SETUP
    b.plugin_task.start()
    await b.plugin_task.wait()

    mock_connected.assert_called_once()
    mock_setup.assert_called_once()


def test_coro_inspection() -> None:
    p = BaseConnectionPlugin('test')

    # -------------------------------------------------------------------------
    # Check args
    #
    async def coro() -> None:
        pass

    assert PluginCallbackHandler._get_coro_kwargs(p, coro) == ()

    async def coro(connection) -> None:
        pass

    assert PluginCallbackHandler._get_coro_kwargs(p, coro) == ('connection', )

    async def coro(connection, context) -> None:
        pass

    assert PluginCallbackHandler._get_coro_kwargs(p, coro) == ('connection', 'context')

    # typo in definition
    async def coro(connection, contrxt) -> None:
        pass

    with pytest.raises(ValueError) as e:
        PluginCallbackHandler._get_coro_kwargs(p, coro)
    assert str(e.value) == 'Invalid parameter name "contrxt" for test.coro'
