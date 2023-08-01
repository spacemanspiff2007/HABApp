from unittest.mock import Mock

import pytest

from HABApp.core.connections import BaseConnectionPlugin, BaseConnection, PluginCallbackHandler
from HABApp.core.connections._definitions import PluginReturn
from HABApp.core.connections.status_transitions import StatusTransitions, ConnectionStatus


def test_transitions():
    status = StatusTransitions()

    def get_flow() -> list[str]:
        ret = []
        while add := status.advance_status():
            ret.append(add.value)
        return ret

    status.setup = True
    assert get_flow() == ['SETUP']

    # Error Handling
    for initial_state in (ConnectionStatus.CONNECTING, ConnectionStatus.CONNECTED, ConnectionStatus.ONLINE):
        status = StatusTransitions()
        status.status = initial_state
        status.setup = True

        assert get_flow() == ['DISCONNECTED', 'OFFLINE', 'SETUP']

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


async def test_plugin_callback():

    sentinel = object()
    mock_connected = Mock()
    mock_setup = Mock()

    class TestPlugin(BaseConnectionPlugin):
        def __init__(self):
            super().__init__('asdf', 0)

        async def on_connected(self, context):
            assert context is sentinel
            mock_connected()

        async def on_disconnected(self) -> PluginReturn:
            pass

        async def on_setup(self, context, connection) -> PluginReturn | None:
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


def test_coro_inspection():
    p = BaseConnectionPlugin('test')

    # -------------------------------------------------------------------------
    # Check args
    #
    async def coro():
        pass

    assert PluginCallbackHandler._get_coro_kwargs(p, coro) == ()

    async def coro(connection):
        pass

    assert PluginCallbackHandler._get_coro_kwargs(p, coro) == ('connection', )

    async def coro(connection, context):
        pass

    assert PluginCallbackHandler._get_coro_kwargs(p, coro) == ('connection', 'context')

    # typo in definition
    async def coro(connection, contrxt):
        pass

    with pytest.raises(ValueError) as e:
        PluginCallbackHandler._get_coro_kwargs(p, coro)
    assert str(e.value) == 'Invalid parameter name "contrxt" for test.coro'

    # -------------------------------------------------------------------------
    # Check return type
    #
    async def coro() -> bool:
        pass

    with pytest.raises(ValueError) as e:
        PluginCallbackHandler._get_coro_kwargs(p, coro)
    assert str(e.value) == 'Coroutine function must return PluginReturn or Optional[PluginReturn]'


async def test_call_order():

    calls = []

    class TestPlugin(BaseConnectionPlugin):
        async def on_connected(self):
            calls.append(self.plugin_name)

    p1 = TestPlugin('p1', -10)
    ph = TestPlugin('handler', 0)
    p3 = TestPlugin('p2', 10)

    b = BaseConnection('test')
    b.register_plugin(p1).register_plugin(ph).register_plugin(p3)

    b.status.status = ConnectionStatus.CONNECTED
    b.plugin_task.start()
    await b.plugin_task.wait()

    assert calls == [ph.plugin_name, p3.plugin_name, p1.plugin_name]
