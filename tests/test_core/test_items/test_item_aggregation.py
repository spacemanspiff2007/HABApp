import asyncio
from asyncio import TaskGroup

import pytest
from pytest import MonkeyPatch

import HABApp
from HABApp import Rule
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import AggregationItem, Item
from HABApp.core.provider import HABAPP_PROVIDER
from tests.rule_runner import SimpleRuleRunner


def _setup(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setitem(HABAPP_PROVIDER._created, ItemRegistry, HABApp.core.Items)
    monkeypatch.setitem(HABAPP_PROVIDER._created, EventBus, HABApp.core.EventBus)


@pytest.mark.no_internals
async def test_aggregation_item(monkeypatch) -> None:

    class TestAggregation(Rule):
        async def test_agg(self) -> None:
            agg = AggregationItem.get_create_item('MyAggregation')
            src = Item.get_create_item('MySource')

            INTERVAL = 0.2

            agg.aggregation_period(INTERVAL * 6)
            agg.aggregation_source(src)
            agg.aggregation_func(lambda x: (max(x), list(x)))

            async def post_val(t, v) -> None:
                await asyncio.sleep(t)
                src.post_value(v)

            async with TaskGroup() as tg:

                tg.create_task(post_val(1 * INTERVAL, 1))
                tg.create_task(post_val(2 * INTERVAL, 3))
                tg.create_task(post_val(3 * INTERVAL, 5))
                tg.create_task(post_val(4 * INTERVAL, 4))
                tg.create_task(post_val(5 * INTERVAL, 2))

                await asyncio.sleep(INTERVAL + INTERVAL / 2)
                assert agg.value == (1, [1])

                await asyncio.sleep(INTERVAL)
                assert agg.value == (3, [1, 3])

                await asyncio.sleep(INTERVAL)
                assert agg.value == (5, [1, 3, 5])

                await asyncio.sleep(INTERVAL * 6)    # 0.6 because the value reaches into the interval!
                assert agg.value == (5, [5, 4, 2])

                await asyncio.sleep(INTERVAL)
                assert agg.value == (4, [4, 2])

                await asyncio.sleep(INTERVAL)
                assert agg.value == (2, [2])

                await asyncio.sleep(INTERVAL)
                assert agg.value == (2, [2])

                await asyncio.sleep(INTERVAL)
                assert agg.value == (2, [2])

    async with SimpleRuleRunner():
        _setup(monkeypatch)
        await TestAggregation().test_agg()


@pytest.mark.no_internals
async def test_aggregation_item_cleanup(monkeypatch) -> None:

    class TestAggregation(Rule):
        async def test_agg(self) -> None:
            agg = AggregationItem.get_create_item('MyTestAggregation')
            src = Item.get_create_item('MyTestSource')

            INTERVAL = 0.2

            agg.aggregation_period(INTERVAL * 6)
            agg.aggregation_source(src)
            agg.aggregation_func(lambda x: list(x))

            async def post_val(t, v) -> None:
                await asyncio.sleep(t)
                src.post_value(v)

            async with TaskGroup() as tg:
                tg.create_task(post_val(1 * INTERVAL, 1))
                tg.create_task(post_val(2 * INTERVAL, 3))
                tg.create_task(post_val(3 * INTERVAL, 5))
                tg.create_task(post_val(4 * INTERVAL, 7))
                tg.create_task(post_val(5 * INTERVAL, 9))

                await asyncio.sleep(INTERVAL / 2)
                await asyncio.sleep(5 * INTERVAL)

                agg.aggregation_period(INTERVAL)
                assert list(agg._vals) == [7, 9]

    async with SimpleRuleRunner():
        _setup(monkeypatch)
        await TestAggregation().test_agg()
