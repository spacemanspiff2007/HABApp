from unittest.mock import Mock

from HABApp.core.connections import BaseConnectionPlugin, BaseConnection
from HABApp.core.connections.status import StatusTransitions, ConnectionStatus


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

        async def on_disconnected(self):
            pass

        async def on_setup(self, context, connection):
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
