from HABApp.core.internals import ItemRegistry
from HABApp.openhab import item_to_reg as item_to_reg_module
from HABApp.openhab.item_to_reg import MEMBERS, add_to_registry, get_members, remove_from_registry
from HABApp.openhab.items import GroupItem, NumberItem, StringItem


def test_get_group_name_to_item(monkeypatch, clean_objs, ir: ItemRegistry) -> None:
    a = ir.add_item(StringItem('a', 1))
    b = ir.add_item(StringItem('b', 'asdf'))
    c = ir.add_item(StringItem('c', (1, 2)))
    d = ir.add_item(StringItem('d'))
    monkeypatch.setitem(MEMBERS, 'test_grp', {d.name, c.name, b.name, a.name})

    assert get_members('test_grp') == (a, b, c, d)


def test_add(monkeypatch, clean_objs) -> None:
    monkeypatch.setattr(item_to_reg_module, 'MEMBERS', {})

    a = StringItem('a', groups={'c', })
    b = StringItem('b', groups={'c', 'does_not_exist'})
    c = GroupItem('c')

    add_to_registry(a)
    add_to_registry(b)
    add_to_registry(c)

    assert get_members('c') == (a, b)
    assert c.members == (a, b)

    assert 'does_not_exist' in item_to_reg_module.MEMBERS
    remove_from_registry(b.name)
    assert get_members('c') == (a, )
    assert 'does_not_exist' not in item_to_reg_module.MEMBERS

    remove_from_registry(c.name)
    add_to_registry(c)

    assert get_members('c') == (a,)
    assert c.members == (a,)

    # test invalid group
    assert get_members('asdf') == ()


def test_update(monkeypatch, clean_objs) -> None:
    monkeypatch.setattr(item_to_reg_module, 'MEMBERS', {})

    a = NumberItem('a')
    add_to_registry(a)

    assert a.label is None
    assert a.dimension is None
    add_to_registry(NumberItem('a', label='asdf', dimension='length'))

    assert a.label == 'asdf'
    assert a.dimension == 'length'
