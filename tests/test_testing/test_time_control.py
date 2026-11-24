# ruff: noqa: F403

import asyncio
import contextlib
from asyncio import CancelledError
from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Final

import pytest
from eascheduler.builder import JobBuilder
from eascheduler.executor import AsyncExecutor

from HABApp.core.asyncio import create_task
from HABApp.testing import UserTimeControl
from HABApp.testing.conftest import *
from HABApp.testing.scheduler import HABAppTestingScheduler


@pytest.fixture
async def create_task_tracked() -> AsyncGenerator[Callable[[Coroutine], None], None]:
    tasks: list[asyncio.Task] = []

    def _create_task(fut: Coroutine) -> None:
        task = create_task(fut)
        tasks.append(task)
        task.add_done_callback(lambda _: tasks.remove(task))

    yield _create_task

    for t in tasks:
        if not t.done():
            t.cancel()
    for t in tasks:
        with contextlib.suppress(CancelledError):
            await t


async def test_single_sleep_is_not_enough_to_drain_a_multi_hop_task_chain(
        time_control: UserTimeControl, create_task_tracked: Callable[[Coroutine], None]
) -> None:
    """Reproduces why a single ``time_control.sleep()`` call is not enough to settle a chain of
    reactive hops: it only does one extra event-loop turn, which lets exactly one already
    scheduled task run. If that task schedules a *new* task (the next hop), the new task only
    gets a chance to run on the *next* turn - so this test fails as long as ``chain_length > 1``.
    """
    chain_length: Final = 10_000
    ran_steps: list[int] = []

    async def hop(step: int) -> None:
        ran_steps.append(step)
        if step + 1 < chain_length:
            create_task_tracked(hop(step + 1))

    create_task_tracked(hop(0))

    await time_control.sleep()

    assert ran_steps == list(range(chain_length))


async def test_advance_drains_a_scheduled_multi_hop_task_chain_repeatedly(
        time_control: UserTimeControl, testing_scheduler: HABAppTestingScheduler,
        create_task_tracked: Callable[[Coroutine], None]
) -> None:
    """A job is scheduled through the (eascheduler based) scheduler to run 2 seconds in the future.
    Once it runs it starts a chain of 200 reactive hops (same pattern as above, chained via
    ``create_task``). ``time_control.advance(2)`` has to both move the clock forward to the point
    where the job fires *and* fully drain the resulting 200-hop chain. This is repeated a second
    time with a newly scheduled job to make sure the mechanism works deterministically more than once.
    """
    job_builder: Final = JobBuilder(testing_scheduler, AsyncExecutor)
    chain_length: Final = 10_000

    ran_steps: list[int] = []

    async def hop(step: int, limit: int) -> None:
        ran_steps.append(step)
        if step + 1 < limit:
            create_task_tracked(hop(step + 1, limit))

    async def start_chain(first_step: int) -> None:
        create_task_tracked(hop(first_step, first_step + chain_length))

    # Nothing has been scheduled yet
    assert ran_steps == []

    # Schedule the first chain 2 seconds in the future
    job_builder.once(2, start_chain, 0)
    job_builder.once(4, start_chain, chain_length)

    await time_control.advance(2)
    assert ran_steps == list(range(chain_length))

    # Schedule a second chain 2 more seconds in the future
    await time_control.advance(2)
    assert ran_steps == list(range(2 * chain_length))
