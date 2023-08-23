from __future__ import annotations

import logging
from typing import Final, Callable, Awaitable, Any

from HABApp.core.lib import SingleTask


class PluginTask(SingleTask):
    def __init__(self, coro: Callable[[], Awaitable[Any]], name: str | None,
                 logger: logging.Logger | None,
                 exception_handler: Callable[[Exception, Callable | str | None], Any]):
        super().__init__(coro, name)

        self.log: Final = logger
        self.exception_handler: Final = exception_handler

    async def _task_wrap(self):
        if self.log is not None:
            self.log.debug(f'Task {self.name} start')

        suffix = ''

        try:
            await super()._task_wrap()
        except Exception as e:
            suffix = ' (with error)'
            self.exception_handler(e, self.name)
        finally:
            if self.log is not None:
                self.log.debug(f'Task {self.name} done {suffix}')
