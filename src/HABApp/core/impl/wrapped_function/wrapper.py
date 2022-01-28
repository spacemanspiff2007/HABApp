import logging
from asyncio import iscoroutinefunction
from typing import Union, Optional, TYPE_CHECKING

from HABApp.core.base import TYPE_WRAPPED_FUNC_OBJ
from HABApp.core.impl.wrapped_function.wrapped_async import TYPE_HINT_FUNC as TYPE_HINT_FUNC_ASYNC
from HABApp.core.impl.wrapped_function.wrapped_async import WrappedAsyncFunction
from HABApp.core.impl.wrapped_function.wrapped_sync import TYPE_HINT_FUNC as TYPE_HINT_FUNC_SYNC
from HABApp.core.impl.wrapped_function.wrapped_sync import WrappedSyncFunction

if TYPE_CHECKING:
    import HABApp


def wrap_func(func: Union[TYPE_HINT_FUNC_SYNC, TYPE_HINT_FUNC_ASYNC],
              warn_too_long=True,
              name: Optional[str] = None,
              logger: Optional[logging.Logger] = None,
              rule_ctx: Optional['HABApp.rule_ctx.HABAppRuleContext'] = None) -> TYPE_WRAPPED_FUNC_OBJ:

    if iscoroutinefunction(func):
        return WrappedAsyncFunction(func, name=name, logger=logger, rule_ctx=rule_ctx)
    else:
        return WrappedSyncFunction(func, warn_too_long=warn_too_long, name=name, logger=logger, rule_ctx=rule_ctx)
