from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Final, override

import pytest

from HABApp.core.internals.function_executor import FunctionExecutorBase
from HABApp.core.internals.function_executor._base import SyncFunctionExecutorBase
from HABApp.core.internals.function_executor.factory import ExecutorFactory
from tests.helpers import TestEventBus


if TYPE_CHECKING:
    import logging
    from collections.abc import AsyncGenerator, Callable, Coroutine

    from HABApp.core.internals import Context, EventBus


class TestingCallableExecutor[**P, R](SyncFunctionExecutorBase[P, R]):

    @override
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
            return None

    @override
    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        try:
            self.func(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
            return None


class TestingCoroExecutor[**P, R](FunctionExecutorBase[P, R]):
    _factory: TestingExecutorFactory

    __slots__ = ('coro', )

    def __init__(self, func: Callable[P, Coroutine[Any, Any, R]], *,
                 name: str | None = None, logger: logging.Logger | None = None,
                 context: Context, factory: TestingExecutorFactory) -> None:
        super().__init__(func, name=name, logger=logger, context=context, factory=factory)
        self.coro: Final = func

    @override
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return await self.coro(*args, **kwargs)
        except Exception as e:
            self.process_exception(e, *args, **kwargs)
            return None

    @override
    def execute_background(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self._factory.tasks.add(
            asyncio.create_task(self.execute(*args, **kwargs), name=self.name)
        )


class TestingExecutorFactory(ExecutorFactory):
    __slots__ = ('tasks', )

    def __init__(self, event_bus: EventBus) -> None:
        super().__init__(event_bus)
        self.tasks: Final[set[asyncio.Task]] = set()

    @override
    def _create_coro_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                     name: str | None = None, logger: logging.Logger | None = None,
                                     context: Context | None = None) -> TestingCoroExecutor[P, R]:
        return TestingCoroExecutor(func, name=name, logger=logger, context=context, factory=self)

    @override
    def _create_function_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                         name: str | None = None, logger: logging.Logger | None = None,
                                         warn_too_long: bool = True,
                                         context: Context | None = None) -> TestingCallableExecutor[P, R]:
        return TestingCallableExecutor(func, name=name, logger=logger, warn_too_long=warn_too_long,
                                       context=context, factory=self)


@pytest.fixture
async def sync_worker(eb: TestEventBus) -> AsyncGenerator[TestingExecutorFactory, Any]:

    factory = TestingExecutorFactory(eb)
    eb.worker_factory = factory
    yield factory

    for task in tuple(factory.tasks):

        try:
            await asyncio.wait_for(task, timeout=1)
        except asyncio.CancelledError:
            pass
