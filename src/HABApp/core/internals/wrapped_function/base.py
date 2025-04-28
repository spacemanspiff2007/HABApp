from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final, Generic, ParamSpec, TypeVar

from HABApp.core.const.topics import TOPIC_ERRORS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.internals import Context, ContextProvidingObj, uses_event_bus
from HABApp.core.lib import format_exception, get_obj_name


if TYPE_CHECKING:
    from collections.abc import Callable


default_logger = logging.getLogger('HABApp.Worker')

event_bus = uses_event_bus()


P = ParamSpec('P')
R = TypeVar('R')


class WrappedFunctionBase(ContextProvidingObj, Generic[P, R]):

    def __init__(self, func: Callable, name: str | None = None, logger: logging.Logger | None = None,
                 context: Context | None = None) -> None:

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

    def run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        raise NotImplementedError()

    async def async_run(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        raise NotImplementedError()

    def process_exception(self, e: Exception, *args: Any, **kwargs: Any) -> None:

        lines = format_exception(e)

        # Log Exception
        self.log.error(f'Error in {self.name:s}: {e}')
        for line in lines:
            self.log.error(line)

        # Create an HABApp event, but only if we are not currently processing an exception while processing an error.
        # Otherwise, we might create an endless loop!
        if not args or not isinstance(args[0], HABAppException):
            event_bus.post_event(
                TOPIC_ERRORS, HABAppException(func_name=self.name, exception=e, traceback='\n'.join(lines))
            )
