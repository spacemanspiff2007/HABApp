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
    agg.aggregation_func(max)

    async def post_val(t, v):
        await asyncio.sleep(t)
        src.post_value(v)


    asyncio.ensure_future(post_val(1 * INTERVAL, 1))
    asyncio.ensure_future(post_val(2 * INTERVAL, 3))
    asyncio.ensure_future(post_val(3 * INTERVAL, 5))
    asyncio.ensure_future(post_val(4 * INTERVAL, 4))
    asyncio.ensure_future(post_val(5 * INTERVAL, 2))

    await asyncio.sleep(INTERVAL + INTERVAL / 2)
    assert agg.value == 1

    await asyncio.sleep(INTERVAL)
    assert agg.value == 3

    await asyncio.sleep(INTERVAL)
    assert agg.value == 5

    await asyncio.sleep(INTERVAL * 6)    # 0.6 because the value reaches into the interval!
    assert agg.value == 5

    await asyncio.sleep(INTERVAL)
    assert agg.value == 4

    await asyncio.sleep(INTERVAL)
    assert agg.value == 2

    await asyncio.sleep(INTERVAL)
    assert agg.value == 2

    await asyncio.sleep(INTERVAL)
    assert agg.value == 2
