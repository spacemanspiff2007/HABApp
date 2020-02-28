from HABApp.util import MultiModeItem

from ..test_core import ItemTests


class TestMultiModeItem(ItemTests):
    CLS = MultiModeItem
    TEST_VALUES = [0, 'str', (1, 2, 3)]


def test_diff_prio():
    p = MultiModeItem('TestItem')
    p.create_mode('modea', 1, '1234')
    p.create_mode('modeb', 2, '4567')

    p1 = p.get_mode('modea')
    p2 = p.get_mode('modeb')

    p1.set_value(5)
    assert p.value == '4567'

    p2.set_enabled(False)
    assert p.value == 5

    p2.set_enabled(True)
    assert p.value == '4567'

    p2.set_enabled(False)
    p2.set_value(8888)
    assert p.value == 8888


def test_calculate_lower_priority_value():
    p = MultiModeItem('TestItem')
    m1 = p.create_mode('modea', 1, '1234')
    m2 = p.create_mode('modeb', 2, '4567')

    assert m1.calculate_lower_priority_value() is None
    assert m2.calculate_lower_priority_value() == '1234'

    m1.set_value('asdf')
    assert m2.calculate_lower_priority_value() == 'asdf'


def test_auto_disable_on():
    p = MultiModeItem('TestItem')
    m1 = p.create_mode('modea', 1, 50)
    m2 = p.create_mode('modeb', 2, 60, auto_disable_on='>')

    m1.set_value(50)
    assert p.value == 60

    m1.set_value(61)
    assert not m2.enabled
    assert p.value == 61

    m1.set_value(59)
    assert p.value == 59


def test_auto_disable_func():
    p = MultiModeItem('TestItem')
    m1 = p.create_mode('modea', 1, 50)
    m2 = p.create_mode('modeb', 2, 60, auto_disable_func=lambda low, s: low == 40)

    m2.set_value(60)
    assert p.value == 60
    assert m2.enabled is True

    m1.set_value(40)

    assert p.value == 40
    assert m2.enabled is False

    m1.set_value(50)
    assert p.value == 50
    assert m2.enabled is False
