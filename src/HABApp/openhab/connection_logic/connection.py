from HABApp.openhab.connection_handler import http_connection
from ._plugin import on_connect, on_disconnect, setup_plugins

log = http_connection.log


def setup():
    from HABApp.runtime import shutdown

    # initialize callbacks
    http_connection.ON_CONNECTED = on_connect
    http_connection.ON_DISCONNECTED = on_disconnect

    # shutdown handler for connection
    shutdown.register_func(http_connection.shutdown_connection, msg='Stopping openHAB connection')

    # shutdown handler for plugins
    shutdown.register_func(on_disconnect, msg='Stopping openHAB plugins')

    # initialize all plugins
    setup_plugins()
    return None


async def start():
    await http_connection.setup_connection()
