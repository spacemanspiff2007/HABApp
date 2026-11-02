from __future__ import annotations

import asyncio
import logging
from asyncio import Task
from typing import TYPE_CHECKING, Any, Final, override

from HABApp.core.internals import Context
from HABApp.core.internals.function_executor import FunctionExecutorBase
from HABApp.core.internals.function_executor._base import SyncFunctionExecutorBase
from HABApp.core.internals.function_executor.factory import ExecutorFactory


if TYPE_CHECKING:
    import logging
    from collections.abc import Callable, Coroutine

    from HABApp.core.internals import Context, EventBus


class HABAppTestingCallableExecutor[**P, R](SyncFunctionExecutorBase[P, R]):
    _factory: HABAppTestingExecutorFactory

    @override
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            self._factory.errors.append(e)
            self.process_exception(e, *args, **kwargs)
            return None

    @override
    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        try:
            self.func(*args, **kwargs)
        except Exception as e:
            self._factory.errors.append(e)
            self.process_exception(e, *args, **kwargs)
            return None


class HABAppTestingCoroExecutor[**P, R](FunctionExecutorBase[P, R]):
    _factory: HABAppTestingExecutorFactory

    __slots__ = ('coro', )

    def __init__(self, func: Callable[P, Coroutine[Any, Any, R]], *,
                 name: str | None = None, logger: logging.Logger | None = None,
                 context: Context, factory: HABAppTestingExecutorFactory) -> None:
        super().__init__(func, name=name, logger=logger, context=context, factory=factory)
        self.coro: Final = func

    @override
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return await self.coro(*args, **kwargs)
        except Exception as e:
            self._factory.errors.append(e)
            self.process_exception(e, *args, **kwargs)
            return None

    @override
    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self._factory.tasks.add(
            asyncio.create_task(self.execute(*args, **kwargs), name=self.name)
        )


class HABAppTestingExecutorFactory(ExecutorFactory):
    __slots__ = ('errors', 'tasks')

    def __init__(self, event_bus: EventBus) -> None:
        super().__init__(event_bus)
        self.errors: Final[list[Exception]] = []
        self.tasks: Final[set[Task]] = set()

    @override
    def _create_coro_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                     name: str | None = None, logger: logging.Logger | None = None,
                                     context: Context | None = None) -> HABAppTestingCoroExecutor[P, R]:
        return HABAppTestingCoroExecutor(
            func, name=name, factory=self, logger=logger,
            context=context,
        )

    @override
    def _create_function_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                         name: str | None = None, logger: logging.Logger | None = None,
                                         warn_too_long: bool = True,
                                         context: Context | None = None) -> HABAppTestingCallableExecutor[P, R]:
        return HABAppTestingCallableExecutor(
            func, name=name, factory=self, warn_too_long=warn_too_long, logger=logger,
            context=context
        )
