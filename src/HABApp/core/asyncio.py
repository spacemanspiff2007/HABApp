from __future__ import annotations

from asyncio import Future as _Future
from asyncio import Task as _Task
from asyncio import run_coroutine_threadsafe as _run_coroutine_threadsafe
from contextvars import ContextVar as _ContextVar
from typing import TYPE_CHECKING
from typing import Any as _Any
from typing import ParamSpec as _ParamSpec
from typing import TypeVar as _TypeVar

from HABApp.core.const import loop


if TYPE_CHECKING:
    from collections.abc import Awaitable as _Awaitable
    from collections.abc import Callable as _Callable
    from collections.abc import Coroutine as _Coroutine


thread_context = _ContextVar('thread_ctx')


class AsyncContextError(Exception):
    def __init__(self, func: _Callable) -> None:
        super().__init__()
        self.func: _Callable = func

    def __str__(self) -> str:
        return f'Function "{self.func.__name__}" may not be called from an async context!'


_tasks = set()


_T = _TypeVar('_T')


def create_task(coro: _Coroutine[_Any, _Any, _T], name: str | None = None) -> _Future[_T]:
    # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
    if thread_context.get(None) is not None:
        f = _run_coroutine_threadsafe(_async_execute_awaitable(coro), loop)
        _tasks.add(f)
        f.add_done_callback(_tasks.discard)
        return f

    t = loop.create_task(coro, name=name)
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)
    return t


def create_task_from_async(coro: _Coroutine[_Any, _Any, _T], name: str | None = None) -> _Task[_T]:
    t = loop.create_task(coro, name=name)
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)
    return t


def run_coro_from_thread(coro: _Coroutine[_Any, _Any, _T], calling: _Callable) -> _T:
    # This function call is blocking, so it can't be called in the async context
    if thread_context.get(None) is None:
        raise AsyncContextError(calling)

    fut = _run_coroutine_threadsafe(_async_execute_awaitable(coro), loop)
    return fut.result()


_P = _ParamSpec('_P')


def run_func_from_async(func: _Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> _T:
    # we already have an async context
    if thread_context.get(None) is None:
        return func(*args, **kwargs)

    # we are in a thread, that's why we can wait (and block) for the future
    future = _run_coroutine_threadsafe(_async_execute_func(func, *args, **kwargs), loop)
    return future.result()


async def _async_execute_func(func: _Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> _T:
    ctx = thread_context.set(None)

    try:
        return func(*args, **kwargs)
    finally:
        thread_context.reset(ctx)


async def _async_execute_awaitable(awaitable: _Awaitable[_T]) -> _T:
    ctx = thread_context.set(None)

    try:
        return await awaitable
    finally:
        thread_context.reset(ctx)
