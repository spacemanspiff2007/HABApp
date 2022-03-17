import logging
from asyncio import iscoroutinefunction
from typing import Union, Optional

from HABApp.core.internals import TYPE_CONTEXT_OBJ
from HABApp.core.internals.wrapped_function.base import TYPE_WRAPPED_FUNC_OBJ
from HABApp.core.internals.wrapped_function.wrapped_async import TYPE_HINT_FUNC_ASYNC, WrappedAsyncFunction
from HABApp.core.internals.wrapped_function.wrapped_sync import TYPE_HINT_FUNC_SYNC, WrappedSyncFunction


def wrap_func(func: Union[TYPE_HINT_FUNC_SYNC, TYPE_HINT_FUNC_ASYNC],
              warn_too_long=True,
              name: Optional[str] = None,
              logger: Optional[logging.Logger] = None,
              context: Optional[TYPE_CONTEXT_OBJ] = None) -> TYPE_WRAPPED_FUNC_OBJ:

    if iscoroutinefunction(func):
        return WrappedAsyncFunction(func, name=name, logger=logger, context=context)
    else:
        return WrappedSyncFunction(func, warn_too_long=warn_too_long, name=name, logger=logger, context=context)
