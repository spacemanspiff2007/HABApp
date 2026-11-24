# ruff: noqa: F403

import asyncio
import contextlib
from asyncio import CancelledError
from collections.abc import Coroutine
from typing import Final

from HABApp.core.asyncio import create_task
from HABApp.testing import UserTimeControl
from HABApp.testing.conftest import *


async def test_single_sleep_is_not_enough_to_drain_a_multi_hop_task_chain(time_control: UserTimeControl) -> None:
    """Reproduces why a single ``time_control.sleep()`` call is not enough to settle a chain of
    reactive hops: it only does one extra event-loop turn, which lets exactly one already
    scheduled task run. If that task schedules a *new* task (the next hop), the new task only
    gets a chance to run on the *next* turn - so this test fails as long as ``chain_length > 1``.
    """
    tasks: list[asyncio.Future] = []
    chain_length: Final = 100
    ran_steps: list[int] = []

    def _create_task(fut: Coroutine) -> None:
        task = create_task(fut)
        tasks.append(task)
        task.add_done_callback(lambda _: tasks.remove(task))

    async def hop(step: int) -> None:
        ran_steps.append(step)
        if step + 1 < chain_length:
            _create_task(hop(step + 1))

    _create_task(hop(0))

    await time_control.sleep()

    try:
        assert ran_steps == list(range(chain_length))
    finally:
        for t in tasks:
            if not t.done():
                t.cancel()
        for t in tasks:
            with contextlib.suppress(CancelledError):
                await t
