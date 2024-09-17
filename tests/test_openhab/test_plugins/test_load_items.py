import logging
from json import dumps

import msgspec.json
from whenever import Instant

import HABApp.openhab.connection.plugins.load_items as load_items_module
from HABApp.core.internals import ItemRegistry
from HABApp.openhab.connection.connection import OpenhabContext
from HABApp.openhab.connection.plugins import LoadOpenhabItemsPlugin
from HABApp.openhab.definitions.rest import ItemResp, ShortItemResp, ThingResp
from HABApp.openhab.definitions.rest.things import ThingStatusResp
from HABApp.openhab.items import Thing


async def _mock_get_all_items():
    resp = [
        {
            'link': 'link length',
            'state': 'NULL',
            'stateDescription': {
                'pattern': '%d',
                'readOnly': True,
                'options': []
            },
            'metadata': {
                'autoupdate': {
                    'value': 'false'
                }
            },
            'editable': False,
            'type': 'Number:Length',
            'name': 'ItemLength',
            'label': 'Label length',
            'tags': [],
            'groupNames': ['grp1']
        },
        {
            'link': 'link plain',
            'state': 'NULL',
            'editable': False,
            'type': 'Number',
            'name': 'ItemPlain',
            'label': 'Label plain',
            'tags': [],
            'groupNames': []
        },
        {
            'link': 'link no update',
            'state': 'NULL',
            'editable': False,
            'type': 'Number',
            'name': 'ItemNoUpdate',
            'tags': [],
            'groupNames': []
        },
    ]

    return msgspec.json.decode(dumps(resp), type=list[ItemResp])


async def _mock_get_all_items_state():
    return [
        ShortItemResp('Number:Length', 'ItemLength', '5 m'),
        ShortItemResp('Number', 'ItemPlain', '3.14')
    ]


async def _mock_get_empty():
    return []


async def _mock_raise():
    raise ValueError()


async def test_item_sync(monkeypatch, ir: ItemRegistry, test_logs):
    monkeypatch.setattr(load_items_module, 'async_get_items', _mock_get_all_items)
    monkeypatch.setattr(load_items_module, 'async_get_all_items_state', _mock_get_all_items_state)
    monkeypatch.setattr(load_items_module, 'async_get_things', _mock_get_empty)

    context = OpenhabContext.new_context(version=(1, 0, 0), session=None, session_options=None,)

    # initial item create
    await LoadOpenhabItemsPlugin().on_connected(context)

    # sync state
    await LoadOpenhabItemsPlugin().on_connected(context)

    assert [(i.name, i.value) for i in ir.get_items()] == [
        ('ItemLength', 5), ('ItemPlain', 3.14), ('ItemNoUpdate', None)]

    test_logs.add_expected('HABApp.openhab.items', logging.WARNING,
                           'Item ItemLength is a UoM item but "unit" is not found in item metadata')


async def test_thing_sync(monkeypatch, ir: ItemRegistry, test_logs):
    monkeypatch.setattr(load_items_module, 'async_get_items', _mock_get_empty)
    monkeypatch.setattr(load_items_module, 'async_get_all_items_state', _mock_raise)

    things_resp: list[ThingResp] = []

    async def _mock_ret():
        return things_resp

    monkeypatch.setattr(load_items_module, 'async_get_things', _mock_ret)

    t1 = ThingResp(
        uid='thing_1', thing_type='thing_type_1', editable=True, status=ThingStatusResp(
            status='ONLINE', detail='NONE', description=''
        )
    )

    t2 = ThingResp(
        uid='thing_2', thing_type='thing_type_2', editable=True, status=ThingStatusResp(
            status='OFFLINE', detail='NONE', description=''
        )
    )

    things_resp = [t1, t2]

    context = OpenhabContext.new_context(version=(1, 0, 0), session=None, session_options=None,)

    # initial thing create
    await LoadOpenhabItemsPlugin().on_connected(context)

    ir_thing = ir.get_item('thing_2')
    assert isinstance(ir_thing, Thing)
    assert ir_thing.status_description == ''

    ir_thing._last_update.set(Instant.from_utc(2001, 1, 1))
    t2.status.description = 'asdf'

    # sync state
    await LoadOpenhabItemsPlugin().on_connected(context)

    assert ir.get_item('thing_2').status_description == 'asdf'

    assert test_logs.copy().set_min_level(10).update().get_messages() == [
        '   [HABApp.openhab.items] | DEBUG | Requesting items',
        '   [HABApp.openhab.items] | DEBUG | Got response with 0 items',
        '   [HABApp.openhab.items] | INFO  | Updated 0 Items',
        '   [HABApp.openhab.items] | DEBUG | Requesting things',
        '   [HABApp.openhab.items] | DEBUG | Got response with 2 things',
        '   [        HABApp.Items] | DEBUG | Added thing_1 (Thing)',
        '   [        HABApp.Items] | DEBUG | Added thing_2 (Thing)',
        '   [HABApp.openhab.items] | INFO  | Updated 2 Things',
        '   [HABApp.openhab.items] | DEBUG | Starting Thing sync',
        '   [HABApp.openhab.items] | DEBUG | Re-synced thing_2',
        '   [HABApp.openhab.items] | DEBUG | Thing sync complete',
        '   [HABApp.openhab.items] | DEBUG | Starting Thing sync',
        '   [HABApp.openhab.items] | DEBUG | Thing sync complete',
    ]
