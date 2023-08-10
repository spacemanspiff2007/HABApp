from __future__ import annotations

import re
from asyncio import CancelledError
from inspect import getmembers
from typing import Final, TYPE_CHECKING, Callable

import HABApp
from HABApp.core.connections._definitions import ConnectionStatus, connection_log
from HABApp.core.connections.status_transitions import StatusTransitions
from HABApp.core.lib import SingleTask
from ..wrapper import process_exception

if TYPE_CHECKING:
    from .base_plugin import BaseConnectionPlugin
    from .plugin_callback import PluginCallbackHandler


class AlreadyHandledException(Exception):
    pass


class HandleExceptionInConnection:
    def __init__(self, connection: BaseConnection, func_name: Callable):
        self._connection: Final = connection
        self._func_name: Final = func_name

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # no exception -> we exit gracefully
        if exc_type is None and exc_val is None:
            return True

        if isinstance(exc_val, CancelledError):
            return None

        self._connection.process_exception(exc_val, self._func_name)
        raise AlreadyHandledException from None


class BaseConnection:
    def __init__(self, name: str):
        self.name: Final = name
        self.log: Final = connection_log.getChild(name)
        self.status: Final = StatusTransitions()

        # this can be an arbitrary obj that can be reused
        self.context = None

        # Plugin handling
        self.plugins: list[BaseConnectionPlugin] = []
        self.plugin_callbacks: dict[ConnectionStatus, list[PluginCallbackHandler]] = {
            name: [] for name in ConnectionStatus}

        # Tasks
        self.plugin_task: Final = SingleTask(self._task_plugin, f'{name.title():s}PluginTask')
        self.advance_status_task: Final = SingleTask(self._task_next_status, f'{name.title():s}AdvanceStatusTask')

    @property
    def is_online(self) -> bool:
        return self.status.status == ConnectionStatus.ONLINE

    @property
    def is_connected(self) -> bool:
        return self.status.status == ConnectionStatus.CONNECTED

    @property
    def is_disconnected(self) -> bool:
        return self.status.status == ConnectionStatus.DISCONNECTED

    @property
    def is_shutdown(self) -> bool:
        return self.status.status == ConnectionStatus.SHUTDOWN

    @property
    def has_errors(self) -> bool:
        return self.status.error

    def handle_exception(self, func: Callable) -> HandleExceptionInConnection:
        return HandleExceptionInConnection(self, func)

    def is_silent_exception(self, e: Exception):
        return False

    def process_exception(self, e: Exception, func: Callable | str):
        self.set_error()

        if self.is_silent_exception(e):
            name = func if isinstance(func, str) else func.__qualname__
            self.log.debug(f'Error in {name:s}: {e}')
        else:
            process_exception(func, e, self.log)

    def register_plugin(self, obj: BaseConnectionPlugin):
        from .plugin_callback import PluginCallbackHandler

        # Check that it's not already registered
        assert not obj.plugin_callbacks

        for p in self.plugins:
            if p.plugin_name == obj.plugin_name:
                raise ValueError(f'Plugin with the same name already registered: {p}')
            if p.plugin_priority == obj.plugin_priority:
                raise ValueError(f'Plugin with priority {p.plugin_priority:d} already registered: {p}')

        name_to_status = {obj.lower(): obj for obj in ConnectionStatus}
        name_regex = re.compile(f'_?on_({"|".join(name_to_status)})(?:__\\w+)?')

        for m_name, member in getmembers(obj, predicate=lambda x: callable(x)):
            if not m_name.lower().startswith('on_') and not m_name.lower().startswith('_on'):
                continue

            if (m := name_regex.fullmatch(m_name)) is None:
                raise ValueError(f'Invalid name: {m_name} in {obj.plugin_name}')

            step = name_to_status[m.group(1)]
            cb = PluginCallbackHandler.create(obj, member)

            dst = self.plugin_callbacks[step]
            assert cb not in dst
            dst.append(cb)

            # sort plugins
            dst.sort(key=lambda x: x.sort_func(step), reverse=True)

        obj.plugin_connection = self
        self.plugins.append(obj)

        self.log.debug(f'Added plugin {obj.plugin_name:s}')
        return self

    def _new_status(self, status: ConnectionStatus):
        self.log.debug(status.value)

        assert not self.plugin_task.is_running
        self.plugin_task.start()

    async def _task_next_status(self):
        with HABApp.core.wrapper.ExceptionToHABApp(logger=self.log):

            # if we are currently running stop the task
            await self.plugin_task.cancel_wait()

            while (next_value := self.status.advance_status()) is not None:
                self._new_status(next_value)
                await self.plugin_task.wait()

        self.advance_status_task.task = None

    async def _task_plugin(self):
        status = self.status
        status_enum = status.status

        self.log.debug(f'Task {status_enum.value:s} start')

        callbacks = self.plugin_callbacks[status_enum]
        for cb in callbacks:

            error = True

            try:
                await cb.run(self, self.context)
                error = False
            except AlreadyHandledException:
                pass
            except Exception as e:
                self.process_exception(e, cb.coro)

            if error:
                # Fail fast during connection
                if status.is_connecting_or_connected():
                    break

        self.log.debug(f'Task {status_enum.value:s} done')

    def clear_error(self):
        if not self.status.error:
            return None
        self.log.debug('Cleared error')
        self.status.error = False

    def set_error(self):
        if self.status.error:
            self.log.debug('Error on connection status is already set')
        else:
            self.status.error = True
            self.log.debug('Set error on connection status')
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def status_from_setup_to_disabled(self):
        self.status.from_setup_to_disabled()
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def status_from_connected_to_disconnected(self):
        self.status.from_connected_to_disconnected()
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def status_configuration_changed(self):
        self.log.debug('Requesting setup')
        self.status.setup = True
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def application_shutdown(self):
        if self.status.shutdown:
            return None
        self.log.debug('Requesting shutdown')
        self.status.shutdown = True
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def application_startup_complete(self):
        self.log.debug('Overview')
        for name, objs in self.plugin_callbacks.items():
            if not objs:
                continue
            self.log.debug(f' - {name}: {", ".join(f"{obj.plugin.plugin_name}.{obj.coro.__name__}" for obj in objs)}')

        self.status.setup = True
        self.advance_status_task.start_if_not_running(run_wrapped=False)
