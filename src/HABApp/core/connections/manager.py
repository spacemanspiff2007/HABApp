from __future__ import annotations

import asyncio
from typing import Final, TypeVar

import HABApp
from HABApp.core.connections import BaseConnection
from HABApp.core.connections._definitions import connection_log


T = TypeVar('T', bound=BaseConnection)


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, BaseConnection] = {}

    def add(self, connection: T) -> T:
        assert connection.name not in self.connections
        self.connections[connection.name] = connection
        connection_log.debug(f'Added {connection.name:s}')

        return connection

    def get(self, name: str) -> BaseConnection:
        return self.connections[name]

    def remove(self, name):
        con = self.get(name)
        if not con.is_shutdown:
            raise ValueError()
        self.connections.pop(name)

    async def on_application_shutdown(self):
        for c in self.connections.values():
            c.on_application_shutdown()

        tasks = [t.advance_status_task.wait() for t in self.connections.values()]
        await asyncio.gather(*tasks)

    def application_startup_complete(self):
        for c in self.connections.values():
            with HABApp.core.wrapper.ExceptionToHABApp(logger=c.log):
                c.application_startup_complete()

    def __repr__(self):
        return f'<{self.__class__.__name__}>'


connection_manager: Final = ConnectionManager()
