from __future__ import annotations

from typing import Final

from HABApp.core.connections import BaseConnection
from HABApp.core.connections.status import connection_log


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, BaseConnection] = {}

    def add(self, name: str, connection: BaseConnection):
        assert name not in self.connections
        self.connections[name] = connection
        connection_log.debug(f'Added {name:s}')

    def get(self, name: str) -> BaseConnection:
        return self.connections[name]

    def remove(self, name):
        con = self.get(name)
        if not con.is_shutdown():
            raise ValueError()
        self.connections.pop(name)

    def shutdown_all(self):
        for c in self.connections.values():
            c.request_shutdown()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


connection_manager: Final = ConnectionManager()
