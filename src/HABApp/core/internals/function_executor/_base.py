from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from HABApp.core.const.topics import TOPIC_ERRORS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.internals import Context, ContextProvidingObj
from HABApp.core.lib import format_exception, get_obj_name


if TYPE_CHECKING:
    from collections.abc import Callable

    from HABApp.core.internals.function_executor.factory import ExecutorFactory


default_logger: Final = logging.getLogger('HABApp.Worker')


class FunctionExecutorBase[**P, R](ContextProvidingObj):
    __slots__ = ('_factory', 'log', 'name')

    def __init__(self, func: Callable[P, R], *,
                 name: str | None = None, logger: logging.Logger | None = None,
                 context: Context, factory: ExecutorFactory) -> None:

        # Allow setting of the rule context
        super().__init__(context)

        # name of the function
        if name is None:
            if self._habapp_ctx is not None:
                name = self._habapp_ctx.get_callback_name(func)
            if name is None:
                name = get_obj_name(func)
        self.name: Final[str] = name

        # Allow custom logger
        self.log: Final = default_logger if logger is None else logger
        self._factory: Final = factory

    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        raise NotImplementedError()

    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        raise NotImplementedError()

    def process_exception(self, e: Exception, *args: Any, **kwargs: Any) -> None:

        lines: Final = format_exception(e)

        # Log Exception
        self.log.error(f'Error in {self.name:s}: {e}')
        for line in lines:
            self.log.error(line)

        # Create an HABApp event, but only if we are not currently processing an exception while processing an error.
        # Otherwise, we might create an endless loop!
        if not args or not isinstance(args[0], HABAppException):
            self._factory.event_bus.post_event(
                TOPIC_ERRORS, HABAppException(func_name=self.name, exception=e, traceback='\n'.join(lines))
            )


class SyncFunctionExecutorBase[**P, R](FunctionExecutorBase[P, R]):
    __slots__ = ('func', 'warn_too_long')

    def __init__(self, func: Callable[P, R], *,
                 name: str | None = None, logger: logging.Logger | None = None, warn_too_long: bool = True,
                 context: Context, factory: ExecutorFactory) -> None:
        super().__init__(func, name=name, logger=logger, context=context, factory=factory)

        self.func: Final = func
        self.warn_too_long: Final = warn_too_long
