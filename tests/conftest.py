import functools
import typing

import asyncio
import pytest

import HABApp
from .helpers import params, parent_rule, sync_worker, event_bus


if typing.TYPE_CHECKING:
    parent_rule = parent_rule
    params = params
    sync_worker = sync_worker
    event_bus = event_bus


def raise_err(func):
    # return async wrapper
    if asyncio.iscoroutinefunction(func) or asyncio.iscoroutine(func):
        @functools.wraps(func)
        async def a(*args, **kwargs):
            return await func(*args, **kwargs)
        return a

    @functools.wraps(func)
    def f(*args, **kwargs):
        return func(*args, **kwargs)

    return f


@pytest.fixture(autouse=True, scope='function')
def show_errors(monkeypatch):
    monkeypatch.setattr(HABApp.core.wrapper, 'ignore_exception', raise_err)
    monkeypatch.setattr(HABApp.core.wrapper, 'log_exception', raise_err)

    HABApp.core.EventBus.remove_all_listeners()


@pytest.yield_fixture(autouse=True, scope='function')
def event_loop():
    yield HABApp.core.const.loop
