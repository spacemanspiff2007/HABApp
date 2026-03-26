from unittest.mock import Mock

from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
from HABApp.openhab.items import GroupItem, NumberItem, StringItem


def test_get_group_name_to_item(ir: ItemRegistry) -> None:
    handler = OhItemRegistryHandler(ir)

    a = StringItem('a', 1, groups=frozenset(('test_grp',)), event_bus=Mock(EventBus))
    b = StringItem('b', 'asdf', groups=frozenset(('test_grp',)), event_bus=Mock(EventBus))
    c = StringItem('c', (1, 2), groups=frozenset(('test_grp',)), event_bus=Mock(EventBus))
    d = StringItem('d', groups=frozenset(('test_grp',)), event_bus=Mock(EventBus))

    handler.add_to_registry(a)
    handler.add_to_registry(b)
    handler.add_to_registry(c)
    handler.add_to_registry(d)

    assert handler.get_group_members('test_grp') == (a, b, c, d)


def test_add(ir) -> None:
    handler = OhItemRegistryHandler(ir)

    a = StringItem('a', groups=frozenset(('c', )), event_bus=Mock(EventBus))
    b = StringItem('b', groups=frozenset(('c', 'does_not_exist')), event_bus=Mock(EventBus))
    c = GroupItem('c', registry_handler=handler, event_bus=Mock(EventBus))

    handler.add_to_registry(a)
    handler.add_to_registry(b)
    handler.add_to_registry(c)

    assert handler.get_group_members('c') == (a, b)
    assert c.members == (a, b)

    assert 'does_not_exist' in handler._group_members
    handler.remove_from_registry(b.name)
    assert handler.get_group_members('c') == (a, )
    assert 'does_not_exist' not in handler._group_members

    handler.remove_from_registry(c.name)
    handler.add_to_registry(c)

    assert handler.get_group_members('c') == (a, )
    assert c.members == (a, )

    # test invalid group
    assert handler.get_group_members('asdf') == ()


def test_update(ir) -> None:
    handler = OhItemRegistryHandler(ir)

    a = NumberItem('a', event_bus=Mock(EventBus))
    handler.add_to_registry(a)

    assert a.label is None
    assert a.dimension is None
    handler.add_to_registry(NumberItem('a', label='asdf', dimension='length', event_bus=Mock(EventBus)))

    assert a.label == 'asdf'
    assert a.dimension == 'length'
