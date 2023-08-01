from __future__ import annotations

from inspect import getmembers
from typing import Final, TYPE_CHECKING

import HABApp
from HABApp.core.lib import SingleTask
from ._definitions import ConnectionStatus, connection_log, RETURN_ERROR
from .status_transitions import StatusTransitions

if TYPE_CHECKING:
    from .base_plugin import BaseConnectionPlugin
    from .plugin_callback import PluginCallbackHandler


class BaseConnection:
    def __init__(self, name: str):
        self.name: Final = name
        self.log: Final = connection_log.getChild(name)

        self.status: Final = StatusTransitions()

        self.context = None

        self.plugins: list[BaseConnectionPlugin] = []
        self.plugin_callbacks: dict[ConnectionStatus, list[PluginCallbackHandler]] = {
            name: [] for name in ConnectionStatus}

        self.plugin_task: Final = SingleTask(self._task_plugin, f'{name.title():s}PluginTask')
        self.advance_status_task: Final = SingleTask(self._task_next_status, f'{name.title():s}AdvanceStatusTask')

    def register_plugin(self, obj: BaseConnectionPlugin):
        from .plugin_callback import PluginCallbackHandler

        # Check that it's not already registered
        assert not obj.plugin_callbacks

        for p in self.plugins:
            if p.plugin_name == obj.plugin_name:
                raise ValueError(f'Plugin with the same name already registered: {p}')
            if p.plugin_priority == obj.plugin_priority:
                raise ValueError(f'Plugin with priority {p.plugin_priority:d} already registered: {p}')

        valid_names = {f'on_{obj.lower():s}': obj for obj in ConnectionStatus}
        for m_name, member in getmembers(obj, predicate=lambda x: callable(x)):
            if not m_name.lower().startswith('on_'):
                continue

            name = valid_names[m_name]
            cb = PluginCallbackHandler.create(obj, member)

            assert name not in obj.plugin_callbacks
            obj.plugin_callbacks[name] = cb

            dst = self.plugin_callbacks[name]
            assert cb not in dst
            dst.append(cb)

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
        for cb in sorted(callbacks, key=lambda x: x.sort_func(status_enum), reverse=True):
            with wrapper:
                ret = await cb.run(self, self.context)

            # Error handling
            if wrapper.raised_exception or ret is RETURN_ERROR:
                if status.error:
                    self.log.debug('Error on connection status is already set')
                else:
                    status.error = True
                    self.log.debug('Set error on connection status')

                # Fail fast during connection
                if status.is_connecting_or_connected():
                    break

        self.log.debug('Plugin task done')

    def clear_error(self):
        if not self.status.error:
            return None
        self.log.debug('Cleared error')
        self.status.error = False

    def status_from_setup_to_disabled(self):
        self.status.from_setup_to_disabled()
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def status_configuration_changed(self):
        self.log.debug('Requesting setup')
        self.status.setup = True
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def request_shutdown(self):
        if not self.status.shutdown:
            return None
        self.log.debug('Requesting shutdown')
        self.status.shutdown = True
        self.advance_status_task.start_if_not_running(run_wrapped=False)

    def is_shutdown(self):
        return self.status == ConnectionStatus.SHUTDOWN
