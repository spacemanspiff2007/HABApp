import logging
from unittest.mock import Mock

from whenever import Instant

from HABApp.core.internals import ItemRegistry
from HABApp.openhab.connection.connection import OpenhabContext
from HABApp.openhab.connection.handler import OpenHabAsyncInterface
from HABApp.openhab.connection.plugins import LoadOpenhabItemsPlugin
from HABApp.openhab.definitions.rest import ItemRespList, ShortItemResp, ThingResp
from HABApp.openhab.definitions.rest.things import ThingStatusResp
from HABApp.openhab.item_factory import OhItemFactory
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
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

    return ItemRespList.validate_python(resp)


async def _mock_get_all_items_state():
    return [
        ShortItemResp(type='Number:Length', name='ItemLength', state='5 m'),
        ShortItemResp(type='Number', name='ItemPlain', state='3.14')
    ]


async def _mock_get_empty():
    return []


async def _mock_raise():
    raise ValueError()


async def test_item_sync(ir: ItemRegistry, test_logs) -> None:

    mock_if = Mock(OpenHabAsyncInterface)
    mock_if.get_items = _mock_get_all_items
    mock_if.get_items_only_state = _mock_get_all_items_state
    mock_if.get_things = _mock_get_empty

    registry_handler = OhItemRegistryHandler(ir)
    kwargs = {
        'item_factory': OhItemFactory(registry_handler, interface=None, event_bus=None),
        'registry_handler': registry_handler,
        'item_registry': ir,
        'interface': mock_if
    }

    context = OpenhabContext.new_context(version=(1, 0, 0))

    # initial item create
    await LoadOpenhabItemsPlugin(**kwargs).on_connected(context)

    # sync state
    await LoadOpenhabItemsPlugin(**kwargs).on_connected(context)

    assert [(i.name, i.value) for i in ir.get_items()] == [
        ('ItemLength', 5), ('ItemPlain', 3.14), ('ItemNoUpdate', None)]

    test_logs.add_expected('HABApp.openhab.items', logging.WARNING,
                           'Item ItemLength is a UoM item but "unit" is not found in item metadata')


async def test_thing_sync(monkeypatch, ir: ItemRegistry, test_logs, oh_interface) -> None:
    things_resp: list[ThingResp] = []

    async def _mock_ret():
        return things_resp

    mock_if = Mock(OpenHabAsyncInterface)
    mock_if.get_items = _mock_get_empty
    mock_if.get_items_only_state = _mock_get_all_items_state
    mock_if.get_things = _mock_ret

    registry_handler = OhItemRegistryHandler(ir)
    kwargs = {
        'item_factory': OhItemFactory(registry_handler, oh_interface, None),
        'registry_handler': registry_handler,
        'item_registry': ir,
        'interface': mock_if,
    }

    t1 = ThingResp(
        UID='thing_1', thingTypeUID='thing_type_1', editable=True, statusInfo=ThingStatusResp(
            status='ONLINE', statusDetail='NONE', description=''
        )
    )

    t2 = ThingResp(
        UID='thing_2', thingTypeUID='thing_type_2', editable=True, statusInfo=ThingStatusResp(
            status='OFFLINE', statusDetail='NONE', description=''
        )
    )

    things_resp = [t1, t2]
    context = OpenhabContext.new_context(version=(1, 0, 0))

    # initial thing create
    await LoadOpenhabItemsPlugin(**kwargs).on_connected(context)

    ir_thing = ir.get_item('thing_2')
    assert isinstance(ir_thing, Thing)
    assert ir_thing.status_description == ''

    ir_thing._last_update.set(Instant.from_utc(2001, 1, 1))
    t2.status.description = 'asdf'

    # sync state
    await LoadOpenhabItemsPlugin(**kwargs).on_connected(context)

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
