from __future__ import annotations

from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any, Final, override

from HABApp.core.internals.function_executor.callable_executor import CallableExecutor, CallablePoolExecutor
from HABApp.core.internals.function_executor.coroutine_executor import CoroutineExecutor
from HABApp.core.internals.function_executor.thread_pool import HABAppThreadPool
from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    import logging
    from collections.abc import AsyncGenerator, Callable, Coroutine

    from HABApp.config import ApplicationConfig
    from HABApp.core.internals import Context, EventBus
    from HABApp.core.internals.function_executor import FunctionExecutorBase
    from HABApp.core.internals.function_executor._base import SyncFunctionExecutorBase


class ExecutorFactory:
    __slots__ = ('event_bus', )

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus: Final = event_bus

    def _create_coro_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                     name: str | None = None, logger: logging.Logger | None = None,
                                     context: Context | None = None) -> CoroutineExecutor[P, R]:
        raise NotImplementedError()

    def _create_function_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                         name: str | None = None, logger: logging.Logger | None = None,
                                         warn_too_long: bool = True,
                                         context: Context | None = None) -> SyncFunctionExecutorBase[P, R]:
        raise NotImplementedError()

    def create[**P, R](self,
                       func: Callable[P, R] | Callable[P, Coroutine[Any, Any, R]], *,
                       name: str | None = None, logger: logging.Logger | None = None, warn_too_long: bool = True,
                       context: Context | None = None) -> FunctionExecutorBase:

        # Check that it's actually a callable, so we fail fast and not when we try to run the function.
        # Some users pass the result of the function call (e.g. func()) by accident
        # which will inevitably fail once we try to run the function.
        if not callable(func):
            try:
                type_name: str = func.__class__.__name__
            except Exception:
                type_name = type(func)

            msg = f'Callable or coroutine function expected! Got "{func}" (type {type_name:s})'
            raise TypeError(msg)

        if iscoroutinefunction(func):
            return self._create_coro_factory(func, name=name, logger=logger, context=context)
        return self._create_function_factory(func, name=name, logger=logger, warn_too_long=warn_too_long,
                                             context=context)


class SyncExecutorFactory(ExecutorFactory):
    @override
    def _create_coro_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                     name: str | None = None, logger: logging.Logger | None = None,
                                     context: Context | None = None) -> CoroutineExecutor[P, R]:
        return CoroutineExecutor(func, name=name, logger=logger, context=context, factory=self)

    @override
    def _create_function_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                         name: str | None = None, logger: logging.Logger | None = None,
                                         warn_too_long: bool = True,
                                         context: Context | None = None) -> CallableExecutor[P, R]:
        return CallableExecutor(func, name=name, logger=logger, warn_too_long=warn_too_long,
                                context=context, factory=self)


class PoolExecutorFactory(ExecutorFactory):
    __slots__ = ('_config', 'pool',)

    def __init__(self, event_bus: EventBus, config: ApplicationConfig, pool: HABAppThreadPool) -> None:
        super().__init__(event_bus=event_bus)
        self.pool: Final = pool
        self._config: Final = config

    @override
    def _create_coro_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                     name: str | None = None, logger: logging.Logger | None = None,
                                     context: Context | None = None) -> CoroutineExecutor[P, R]:
        return CoroutineExecutor(func, name=name, logger=logger, context=context, factory=self)

    @override
    def _create_function_factory[**P, R](self, func: Callable[P, Coroutine[Any, Any, R]], *,
                                         name: str | None = None, logger: logging.Logger | None = None,
                                         warn_too_long: bool = True,
                                         context: Context | None = None) -> CallablePoolExecutor[P, R]:
        return CallablePoolExecutor(func, name=name, logger=logger, warn_too_long=warn_too_long,
                                    context=context, factory=self)

    async def update_pool(self) -> None:
        executor = await self.pool.update_executor(self._config)
        await self.pool.shutdown_thread_pool_executor(executor)


@HABAPP_PROVIDER.register
async def provide_executor(config: ApplicationConfig, event_bus: EventBus) -> AsyncGenerator[ExecutorFactory, Any]:
    pool_cfg = config.habapp.thread_pool

    if not pool_cfg.enabled:
        yield SyncExecutorFactory(event_bus)

    factory = PoolExecutorFactory(event_bus, config, HABAppThreadPool.create(config))
    pool_cfg.subscribe_for_changes(factory.update_pool)
    yield factory

    await factory.pool.shutdown()
