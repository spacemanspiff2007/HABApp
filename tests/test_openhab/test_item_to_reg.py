from HABApp.core.internals import ItemRegistry
from HABApp.openhab.item_to_reg import MEMBERS, get_members
from HABApp.openhab.items import StringItem


def test_get_members(monkeypatch, clean_objs, ir: ItemRegistry) -> None:
    a = ir.add_item(StringItem('a', 1))
    b = ir.add_item(StringItem('b', 'asdf'))
    c = ir.add_item(StringItem('c', (1, 2)))
    d = ir.add_item(StringItem('d'))
    monkeypatch.setitem(MEMBERS, 'test_grp', {d.name, c.name, b.name, a.name})

    assert get_members('test_grp') == (a, b, c, d)
