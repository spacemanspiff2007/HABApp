import logging
from typing import Optional

import HABApp
from HABApp.core.base import WrappedFunctionBase
from HABApp.core.lib import format_exception

default_logger = logging.getLogger('HABApp.Worker')


class WrappedFunctionBaseImpl(WrappedFunctionBase):

    def __init__(self, func: callable,
                 name: Optional[str] = None,
                 logger: Optional[logging.Logger] = None,
                 rule_ctx: Optional['HABApp.rule_ctx.HABAppRuleContext'] = None):

        # Allow setting of the rule context
        self._habapp_rule_ctx = rule_ctx

        # name of the function
        if name is None:
            if rule_ctx is not None:
                name = rule_ctx.get_callback_name(func)
            if name is None:
                name = func.__name__
        self.name: str = name

        # Allow custom logger
        self.log = default_logger
        if logger:
            self.log = logger

    def process_exception(self, e: Exception, *args, **kwargs):

        lines = format_exception(e)

        # Log Exception
        self.log.error(f'Error in {self.name}: {e}')
        for line in lines:
            self.log.error(line)

        # Create HABApp event, but only if we are not currently processing an exception while processing an error.
        # Otherwise we might create an endless loop!
        if not args or not isinstance(args[0], HABApp.core.events.habapp_events.HABAppException):
            HABApp.core.EventBus.post_event(
                HABApp.core.const.topics.ERRORS, HABApp.core.events.habapp_events.HABAppException(
                    func_name=self.name, exception=e, traceback='\n'.join(lines)
                )
            )
