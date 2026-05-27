import asyncio
import functools
import logging
from collections.abc import Generator
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest

import HABApp
from HABApp.core.files import FileManager
from HABApp.core.internals import EventBus, ItemRegistry, setup_internals
from HABApp.core.items.base_item_times_data import ItemTimesBackup
from HABApp.core.provider import HABAPP_PROVIDER
from tests.helpers import LogCollector, eb, get_dummy_cfg, params, parent_rule, sync_worker
from tests.helpers.log.log_matcher import AsyncDebugWarningMatcher, LogLevelMatcher


if TYPE_CHECKING:
    parent_rule = parent_rule
    params = params
    sync_worker = sync_worker
    eb = eb


def raise_err(func):
    # return async wrapper
    if iscoroutinefunction(func) or asyncio.iscoroutine(func):
        @functools.wraps(func)
        async def a(*args, **kwargs):
            return await func(*args, **kwargs)
        return a

    @functools.wraps(func)
    def f(*args, **kwargs):
        return func(*args, **kwargs)

    return f


@pytest.fixture(autouse=True)
def show_errors(monkeypatch) -> None:
    # Patch the wrapper so that we always raise the exception
    monkeypatch.setattr(HABApp.core.wrapper, 'ignore_exception', raise_err)
    monkeypatch.setattr(HABApp.core.wrapper, 'log_exception', raise_err)


@pytest.fixture(autouse=True)
def item_times_backup() -> Generator[Mock, Any, None]:
    b = Mock(ItemTimesBackup)

    # ToDo: rework the item registry events so we don't have to do this
    if HABAPP_PROVIDER.has_factory(ItemTimesBackup):
        HABAPP_PROVIDER.remove_factory(ItemTimesBackup)

    HABAPP_PROVIDER.add_object(b, ItemTimesBackup)
    yield b
    HABAPP_PROVIDER._created.pop(ItemTimesBackup, None)


@pytest.fixture(autouse=True)
def use_dummy_cfg(monkeypatch):
    cfg = get_dummy_cfg()
    monkeypatch.setattr(HABApp, 'CONFIG', cfg)
    monkeypatch.setattr(HABApp.config, 'CONFIG', cfg)
    monkeypatch.setattr(HABApp.config.config, 'CONFIG', cfg)
    return cfg


@pytest.fixture
def ir() -> Generator[ItemRegistry, Any, None]:
    ir = ItemRegistry()

    # ToDo: rework so we don't have to add it to HABAPP_PROVIDER
    HABAPP_PROVIDER.add_object(ir, ItemRegistry)
    yield ir
    HABAPP_PROVIDER._created.pop(ItemRegistry, None)


@pytest.fixture
def file_manager(eb: EventBus):
    return FileManager(None, eb)


@pytest.fixture(autouse=True)
def clean_objs(ir: ItemRegistry, eb: EventBus, file_manager: FileManager, request):
    markers = request.node.own_markers
    for marker in markers:
        if marker.name == 'no_internals':
            yield None
            return None

    restore = setup_internals(ir, eb, final=False)

    yield

    for r in restore:
        r.restore()


@pytest.fixture(autouse=True)
def test_logs(caplog, request):
    caplog.set_level(logging.DEBUG)

    c = LogCollector(caplog)

    # This seems to be an asyncio issue (that a subprocess can block)
    c.rec_ignored.append(AsyncDebugWarningMatcher())

    yield c

    additional_ignores: list[LogLevelMatcher] = []

    markers = request.node.own_markers
    for marker in markers:
        if marker.name == 'ignore_log_errors':
            additional_ignores.append(LogLevelMatcher(logging.ERROR))
        elif marker.name == 'ignore_log_warnings':
            additional_ignores.append(LogLevelMatcher(logging.WARNING))

    if additional_ignores:
        c.rec_expected.extend(additional_ignores)

    c.assert_ok()
