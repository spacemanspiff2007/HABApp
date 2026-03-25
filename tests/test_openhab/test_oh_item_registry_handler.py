from HABApp.core.internals import ItemRegistry
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
from HABApp.openhab.items import GroupItem, NumberItem, StringItem


def test_get_group_name_to_item(ir: ItemRegistry) -> None:
    handler = OhItemRegistryHandler(ir)

    a = StringItem('a', 1, groups=frozenset(('test_grp',)))
    b = StringItem('b', 'asdf', groups=frozenset(('test_grp',)))
    c = StringItem('c', (1, 2), groups=frozenset(('test_grp',)))
    d = StringItem('d', groups=frozenset(('test_grp',)))

    handler.add_to_registry(a)
    handler.add_to_registry(b)
    handler.add_to_registry(c)
    handler.add_to_registry(d)

    assert handler.get_group_members('test_grp') == (a, b, c, d)


def test_add(ir) -> None:
    handler = OhItemRegistryHandler(ir)

    a = StringItem('a', groups=frozenset(('c', )))
    b = StringItem('b', groups=frozenset(('c', 'does_not_exist')))
    c = GroupItem('c', registry_handler=handler)

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

    a = NumberItem('a')
    handler.add_to_registry(a)

    assert a.label is None
    assert a.dimension is None
    handler.add_to_registry(NumberItem('a', label='asdf', dimension='length'))

    assert a.label == 'asdf'
    assert a.dimension == 'length'
