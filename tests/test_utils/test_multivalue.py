import pytest

from HABApp.util import MultiModeItem
from HABApp.util.multimode_item import BaseMode, ValueModeMode
from ..test_core import ItemTests


class TestMultiModeItem(ItemTests):
    CLS = MultiModeItem
    TEST_VALUES = [0, 'str', (1, 2, 3)]


def test_diff_prio():
    p = MultiModeItem('TestItem')
    p1 = ValueModeMode('modea', '1234')
    p2 = ValueModeMode('modeb', '4567')
    p.add_mode(1, p1).add_mode(2, p2)

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
    m1 = ValueModeMode('modea', '1234')
    m2 = ValueModeMode('modeb', '4567')
    p.add_mode(1, m1).add_mode(2, m2)

    assert m1.calculate_lower_priority_value() is None
    assert m2.calculate_lower_priority_value() == '1234'

    m1.set_value('asdf')
    assert m2.calculate_lower_priority_value() == 'asdf'


def test_auto_disable_1():
    p = MultiModeItem('TestItem')
    m1 = ValueModeMode('modea', 50)
    m2 = ValueModeMode('modeb', 60, auto_disable_func= lambda l, o: l > o)
    p.add_mode(1, m1).add_mode(2, m2)

    m1.set_value(50)
    assert p.value == 60

    m1.set_value(61)
    assert not m2.enabled
    assert p.value == 61

    m1.set_value(59)
    assert p.value == 59


def test_auto_disable_func():
    p = MultiModeItem('TestItem')
    m1 = ValueModeMode('modea', 50)
    m2 = ValueModeMode('modeb', 60, auto_disable_func=lambda low, s: low == 40)
    p.add_mode(1, m1).add_mode(2, m2)

    m2.set_value(60)
    assert p.value == 60
    assert m2.enabled is True

    m1.set_value(40)

    assert p.value == 40
    assert m2.enabled is False

    m1.set_value(50)
    assert p.value == 50
    assert m2.enabled is False


def test_unknown():
    p = MultiModeItem('asdf')
    with pytest.raises(KeyError):
        p.get_mode('asdf')

    p.add_mode(1, BaseMode('mode'))
    with pytest.raises(KeyError):
        p.get_mode('asdf')


def test_remove():
    p = MultiModeItem('asdf')
    m1 = BaseMode('m1')
    m2 = BaseMode('m2')

    p.add_mode(0, m1)
    p.add_mode(1, m2)

    p.remove_mode('m1')

    assert p.all_modes() == [(1, m2)]
