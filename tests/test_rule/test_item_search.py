from unittest.mock import Mock

import pytest

from HABApp import Rule
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import BaseValueItem, Item
from HABApp.openhab.connection.handler import OpenHabSyncInterface
from HABApp.openhab.items import OpenhabItem, SwitchItem
from HABApp.openhab.items.base_item import MetaData
from HABApp.rule.rule_hook import HABAppRuleHook


@pytest.fixture
def rule(ir: ItemRegistry) -> Rule:
    rules = []
    hook = HABAppRuleHook(rules.append, lambda x: x.__class__.__name__, None, None, loop=Mock, async_http_client=None,
                          item_registry=ir, event_bus=Mock(), executor_factory=None,
                          oh_interface_sync=None, oh_interface_async=None,
                          mqtt_interface_async=None, mqtt_interface_sync=None)
    hook.in_dict(globals())
    return Rule()


def test_search_type(ir: ItemRegistry, rule: Rule) -> None:
    item1 = BaseValueItem('item_1', event_bus=Mock(EventBus))
    item2 = Item('item_2', event_bus=Mock(EventBus))

    assert rule.get_items() == []

    ir.add_item(item1)
    ir.add_item(item2)

    assert rule.get_items() == [item1, item2]
    assert rule.get_items(type=BaseValueItem) == [item1, item2]
    assert rule.get_items(type=(BaseValueItem, Item)) == [item1, item2]

    assert rule.get_items(type=Item) == [item2]


def test_search_oh(ir: ItemRegistry, rule: Rule) -> None:
    item1 = OpenhabItem(
        'oh_item_1', tags=frozenset(['tag1', 'tag2', 'tag3']),
        groups=frozenset(['grp1', 'grp2']), metadata={'meta1': MetaData('meta_v1')},
        event_bus=Mock(EventBus), interface=Mock(OpenHabSyncInterface)
    )
    item2 = SwitchItem(
        'oh_item_2', tags=frozenset(['tag1', 'tag2', 'tag4']),
        groups=frozenset(['grp2', 'grp3']), metadata={'meta2': MetaData('meta_v2', config={'a': 'b'})},
        event_bus=Mock(EventBus), interface=Mock(OpenHabSyncInterface)
    )

    item3 = Item('item_2', event_bus=Mock(EventBus))

    assert rule.get_items() == []

    ir.add_item(item1)
    ir.add_item(item2)
    ir.add_item(item3)

    assert rule.get_items() == [item1, item2, item3]
    assert rule.get_items(tags='tag2') == [item1, item2]
    assert rule.get_items(tags='tag4') == [item2]

    assert rule.get_items(groups='grp1') == [item1]
    assert rule.get_items(groups='grp2') == [item1, item2]

    assert rule.get_items(groups='grp1', tags='tag1') == [item1]
    assert rule.get_items(groups='grp2', tags='tag4') == [item2]

    assert rule.get_items(metadata='meta1') == [item1]
    assert rule.get_items(metadata='meta2') == [item2]
    assert rule.get_items(metadata=r'meta\d') == [item1, item2]

    assert rule.get_items(metadata_value='meta_v1') == [item1]
    assert rule.get_items(metadata_value='meta_v2') == [item2]
    assert rule.get_items(metadata_value=r'meta_v\d') == [item1, item2]
    assert rule.get_items(groups='grp1', metadata_value=r'meta_v\d') == [item1]


def test_classcheck(rule: Rule) -> None:
    with pytest.raises(ValueError):
        rule.get_items(Item, tags='asdf')


def test_search_name(ir: ItemRegistry, rule: Rule) -> None:
    item1 = BaseValueItem('item_1a', event_bus=Mock(EventBus))
    item2 = Item('item_2a', event_bus=Mock(EventBus))

    assert rule.get_items() == []

    ir.add_item(item1)
    ir.add_item(item2)

    assert rule.get_items() == [item1, item2]
    assert rule.get_items(name=r'\da') == [item1, item2]
