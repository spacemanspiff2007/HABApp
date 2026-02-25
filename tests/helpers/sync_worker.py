from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import pytest

from HABApp.core.internals.function_executor.testing import TestingExecutorFactory


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from tests.helpers import TestEventBus



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
