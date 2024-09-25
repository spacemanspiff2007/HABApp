from __future__ import annotations

import logging
from collections.abc import Callable

from typing_extensions import override

from HABApp.core.asyncio import async_context, create_task
from HABApp.core.internals import Context
from HABApp.core.internals.wrapped_function.base import P, R, WrappedFunctionBase


class WrappedSyncFunction(WrappedFunctionBase[P, R]):

    def __init__(self, func: Callable,
                 warn_too_long=True,
                 name: str | None = None,
                 logger: logging.Logger | None = None,
                 context: Context | None = None) -> None:

        super().__init__(name=name, func=func, logger=logger, context=context)
        assert callable(func)

        self.func = func
        self.warn_too_long: bool = warn_too_long

    @override
    def run(self, *args: P.args, **kwargs: P.kwargs) -> None:
        create_task(self.async_run(*args, **kwargs), name=self.name)

    @override
    async def async_run(self, *args: P.args, **kwargs: P.kwargs) -> R | None:

        token = async_context.set('WrappedSyncFunction')

        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
        finally:
            async_context.reset(token)
