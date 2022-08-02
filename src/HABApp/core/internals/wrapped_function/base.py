import logging
from typing import Optional, TypeVar, Callable

from HABApp.core.const.topics import TOPIC_ERRORS as TOPIC_ERRORS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.internals import HINT_CONTEXT_OBJ, ContextProvidingObj, uses_event_bus
from HABApp.core.lib import format_exception

default_logger = logging.getLogger('HABApp.Worker')

event_bus = uses_event_bus()


class WrappedFunctionBase(ContextProvidingObj):

    def __init__(self, func: Callable, name: Optional[str] = None, logger: Optional[logging.Logger] = None,
                 context: Optional[HINT_CONTEXT_OBJ] = None):

        # Allow setting of the rule context
        super().__init__(context)

        # name of the function
        if name is None:
            if self._habapp_ctx is not None:
                name = self._habapp_ctx.get_callback_name(func)
            if name is None:
                name = func.__name__
        self.name: str = name

        # Allow custom logger
        self.log = default_logger
        if logger:
            self.log = logger

    def run(self, *args, **kwargs):
        raise NotImplementedError()

    def process_exception(self, e: Exception, *args, **kwargs):

        lines = format_exception(e)

        # Log Exception
        self.log.error(f'Error in {self.name}: {e}')
        for line in lines:
            self.log.error(line)

        # Create HABApp event, but only if we are not currently processing an exception while processing an error.
        # Otherwise we might create an endless loop!
        if not args or not isinstance(args[0], HABAppException):
            event_bus.post_event(
                TOPIC_ERRORS, HABAppException(func_name=self.name, exception=e, traceback='\n'.join(lines))
            )


TYPE_WRAPPED_FUNC_OBJ = TypeVar('TYPE_WRAPPED_FUNC_OBJ', bound=WrappedFunctionBase)
