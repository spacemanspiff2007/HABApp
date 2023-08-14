from __future__ import annotations

import logging
from typing import Final

from HABApp.core.const.const import StrEnum

connection_log = logging.getLogger('HABApp.connection')


class ConnectionStatus(StrEnum):
    STARTUP = 'STARTUP'

    SETUP = 'SETUP'

    # connection flow
    CONNECTING = 'CONNECTING'
    CONNECTED = 'CONNECTED'
    ONLINE = 'ONLINE'

    # unexpected disconnect or error
    DISCONNECTED = 'DISCONNECTED'
    OFFLINE = 'OFFLINE'

    # connection is disabled
    DISABLED = 'DISABLED'

    # normal shutdown flow
    SHUTDOWN = 'SHUTDOWN'


# Handler which manages the connection
CONNECTION_HANDLER_NAME: Final = 'ConnectionHandler'
