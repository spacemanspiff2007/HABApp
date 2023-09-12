from __future__ import annotations

from ._definitions import ConnectionStatus


class StatusTransitions:
    def __init__(self):
        self.status = ConnectionStatus.STARTUP
        self.manual: ConnectionStatus | None = None

        # Flags
        self.error = False
        self.setup = False
        self.shutdown = False

    def advance_status(self) -> ConnectionStatus | None:
        if self.manual is not None:
            self.status = status = self.manual
            self.manual = None
        else:
            if (status := self._next_step()) is None:
                return None
            self.status = status

        return status

    def is_connecting_or_connected(self):
        return self.status in (ConnectionStatus.CONNECTING, ConnectionStatus.CONNECTED, ConnectionStatus.ONLINE)

    def _set_manual(self, status: ConnectionStatus):
        assert self.manual is None
        self.manual = status

    def from_setup_to_disabled(self):
        assert self.status == ConnectionStatus.SETUP
        self._set_manual(ConnectionStatus.DISABLED)

    def from_connected_to_disconnected(self):
        assert self.status == ConnectionStatus.CONNECTED
        self._set_manual(ConnectionStatus.DISCONNECTED)

    def _next_step(self) -> ConnectionStatus:
        status = self.status

        if self.error:
            if self.is_connecting_or_connected():
                return ConnectionStatus.DISCONNECTED
            if status == ConnectionStatus.SETUP:
                return ConnectionStatus.DISABLED

        if self.setup:
            if self.is_connecting_or_connected():
                return ConnectionStatus.DISCONNECTED
            if status in (ConnectionStatus.STARTUP, ConnectionStatus.OFFLINE, ConnectionStatus.DISABLED):
                self.setup = False
                return ConnectionStatus.SETUP

        if self.shutdown:
            if self.is_connecting_or_connected():
                return ConnectionStatus.DISCONNECTED
            if status in (ConnectionStatus.STARTUP, ConnectionStatus.OFFLINE, ConnectionStatus.DISABLED):
                return ConnectionStatus.SHUTDOWN

        # Automatically reconnect if there are no errors
        if not self.error and status is ConnectionStatus.OFFLINE:
            return ConnectionStatus.CONNECTING

        # automatic transitions if no flags are set
        transitions = {
            ConnectionStatus.CONNECTING: ConnectionStatus.CONNECTED,
            ConnectionStatus.CONNECTED: ConnectionStatus.ONLINE,

            ConnectionStatus.DISCONNECTED: ConnectionStatus.OFFLINE,

            ConnectionStatus.SETUP: ConnectionStatus.CONNECTING,
        }
        return transitions.get(status)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.status} ' \
               f'[{"x" if self.error else " "}] Error, ' \
               f'[{"x" if self.setup else " "}] Setup>'

    def __eq__(self, other: ConnectionStatus):
        if not isinstance(other, ConnectionStatus):
            return NotImplemented
        return self.status == other
