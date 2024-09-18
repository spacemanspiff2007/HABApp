from __future__ import annotations

from asyncio import Future as _Future
from asyncio import Task as _Task
from asyncio import run_coroutine_threadsafe as _run_coroutine_threadsafe
from collections.abc import Callable
from collections.abc import Callable as _Callable
from collections.abc import Coroutine as _Coroutine
from contextvars import ContextVar as _ContextVar
from contextvars import Token as _Token
from types import TracebackType
from typing import Any as _Any
from typing import Final
from typing import ParamSpec as _ParamSpec
from typing import TypeVar as _TypeVar

from HABApp.core.const import loop


async_context = _ContextVar('async_ctx')


class AsyncContext:
    def __init__(self, value: str) -> None:
        self.value: Final = value
        self.token: _Token[str] | None = None
        self.parent: AsyncContext | None = None

    def __enter__(self) -> None:
        assert self.token is None, self
        self.parent = async_context.get(None)
        self.token = async_context.set(self.value)

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        async_context.reset(self.token)

    def __repr__(self) -> str:
        parent: str = ''
        if self.parent:
            parent = f'{self.parent} -> '
        return f'<{self.__class__.__name__} {parent:s}{self.value:s}>'


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
    if async_context.get(None) is None:
        f = _run_coroutine_threadsafe(coro, loop)
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
    if async_context.get(None) is not None:
        raise AsyncContextError(calling)

    fut = _run_coroutine_threadsafe(coro, loop)
    return fut.result()


_P = _ParamSpec('_P')


def run_func_from_async(func: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> _T:
    # we already have an async context
    if async_context.get(None) is not None:
        return func(*args, **kwargs)

    future = _run_coroutine_threadsafe(_run_func_from_async_helper(func, *args, **kwargs), loop)
    # Doc build fails if we enable this
    # TODO: Fix the Rule Runner
    return future.result()


async def _run_func_from_async_helper(func: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> _T:
    return func(*args, **kwargs)
