import asyncio
import functools
import typing

import pytest

import HABApp
import tests
from HABApp.core.asyncio import async_context
from HABApp.core.internals import setup_internals, EventBus, ItemRegistry
from .helpers import params, parent_rule, sync_worker, eb, get_dummy_cfg

if typing.TYPE_CHECKING:
    parent_rule = parent_rule
    params = params
    sync_worker = sync_worker
    eb = eb


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


@pytest.yield_fixture(autouse=True, scope='function')
def use_dummy_cfg(monkeypatch):
    cfg = get_dummy_cfg()
    monkeypatch.setattr(HABApp, 'CONFIG', cfg)
    monkeypatch.setattr(HABApp.config, 'CONFIG', cfg)
    monkeypatch.setattr(HABApp.config.config, 'CONFIG', cfg)
    yield


@pytest.yield_fixture(autouse=True, scope='session')
def event_loop():
    token = async_context.set('pytest')

    yield HABApp.core.const.loop

    async_context.reset(token)


@pytest.yield_fixture(scope='function')
def ir():
    ir = ItemRegistry()
    yield ir
    for name in ir.get_item_names():
        ir.pop_item(name)


@pytest.yield_fixture(autouse=True, scope='function')
def clean_objs(ir: ItemRegistry, eb: EventBus):
    restore = setup_internals(ir, eb, final=False)

    yield

    for r in restore:
        r.restore()
