from __future__ import annotations
import re

from inspect import getmembers
from typing import Final, TYPE_CHECKING

import HABApp
from HABApp.core.connections._definitions import ConnectionStatus, connection_log, RETURN_ERROR
from HABApp.core.connections.status_transitions import StatusTransitions
from HABApp.core.lib import SingleTask

if TYPE_CHECKING:
    from .base_plugin import BaseConnectionPlugin
    from .plugin_callback import PluginCallbackHandler


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
        self.log.debug(status)

        assert not self.plugin_task.is_running
        self.log.debug('Plugin task start')
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

        wrapper = HABApp.core.wrapper.ExceptionToHABApp(logger=self.log)

        callbacks = self.plugin_callbacks[status_enum]
        for cb in callbacks:
            with wrapper:
                ret = await cb.run(self, self.context)

            # Error handling
            if wrapper.raised_exception or ret is RETURN_ERROR:
                self.set_error()

                # Fail fast during connection
                if status.is_connecting_or_connected():
                    break

        self.log.debug('Plugin task done')

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
        if not self.status.shutdown:
            return None
        self.log.debug('Requesting shutdown')
        self.status.shutdown = True
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def application_startup_complete(self):
        self.log.debug('Overview')
        for name, objs in self.plugin_callbacks.items():
            if not objs:
                continue
            self.log.debug(f' - {name}: {", ".join(obj.plugin.plugin_name for obj in objs)}')

        self.status.setup = True
        self.advance_status_task.start_if_not_running(run_wrapped=False)
