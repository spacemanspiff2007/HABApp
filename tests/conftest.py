import functools
import typing

import asyncio
import pytest

import HABApp
from .helpers import params, parent_rule, sync_worker, event_bus, get_dummy_cfg


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
    # Patch the wrapper so that we always raise the exception
    monkeypatch.setattr(HABApp.core.wrapper, 'ignore_exception', raise_err)
    monkeypatch.setattr(HABApp.core.wrapper, 'log_exception', raise_err)

    # Delete all existing items/listener from previous tests
    HABApp.core.EventBus.remove_all_listeners()
    for name in HABApp.core.Items.get_all_item_names():
        HABApp.core.Items.pop_item(name)


@pytest.yield_fixture(autouse=True, scope='function')
def use_dummy_cfg(monkeypatch):
    cfg = get_dummy_cfg()
    monkeypatch.setattr(HABApp, 'CONFIG', cfg)
    monkeypatch.setattr(HABApp.config, 'CONFIG', cfg)
    monkeypatch.setattr(HABApp.config.config, 'CONFIG', cfg)
    yield


@pytest.yield_fixture(autouse=True, scope='function')
def event_loop():
    yield HABApp.core.const.loop
