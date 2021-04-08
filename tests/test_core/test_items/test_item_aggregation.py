import asyncio

import pytest

import HABApp


@pytest.mark.asyncio
async def test_aggregation_item():
    agg = HABApp.core.items.AggregationItem.get_create_item('MyAggregation')
    src = HABApp.core.items.Item.get_create_item('MySource')

    INTERVAL = 0.2

    agg.aggregation_period(INTERVAL * 6)
    agg.aggregation_source(src)
    agg.aggregation_func(lambda x: (max(x), list(x)))

    async def post_val(t, v):
        await asyncio.sleep(t)
        src.post_value(v)

    asyncio.create_task(post_val(1 * INTERVAL, 1))
    asyncio.create_task(post_val(2 * INTERVAL, 3))
    asyncio.create_task(post_val(3 * INTERVAL, 5))
    asyncio.create_task(post_val(4 * INTERVAL, 4))
    asyncio.create_task(post_val(5 * INTERVAL, 2))

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


@pytest.mark.asyncio
async def test_aggregation_item_cleanup():
    agg = HABApp.core.items.AggregationItem.get_create_item('MyTestAggregation')
    src = HABApp.core.items.Item.get_create_item('MyTestSource')

    INTERVAL = 0.2

    agg.aggregation_period(INTERVAL * 6)
    agg.aggregation_source(src)
    agg.aggregation_func(lambda x: list(x))

    async def post_val(t, v):
        await asyncio.sleep(t)
        src.post_value(v)

    asyncio.create_task(post_val(1 * INTERVAL, 1))
    asyncio.create_task(post_val(2 * INTERVAL, 3))
    asyncio.create_task(post_val(3 * INTERVAL, 5))
    asyncio.create_task(post_val(4 * INTERVAL, 7))
    asyncio.create_task(post_val(5 * INTERVAL, 9))

    await asyncio.sleep(INTERVAL / 2)
    await asyncio.sleep(5 * INTERVAL)

    agg.aggregation_period(INTERVAL)
    assert list(agg._vals) == [7, 9]
