from typing import Tuple
from unittest.mock import Mock

import pytest

from HABApp.core.const import MISSING
from HABApp.util.multimode import BaseMode, ValueMode, MultiModeItem
from ..test_core import ItemTests
from tests.helpers.parent_rule import DummyRule


class TestMultiModeItem(ItemTests):
    CLS = MultiModeItem
    TEST_VALUES = [0, 'str', (1, 2, 3)]


def test_diff_prio(parent_rule: DummyRule):
    p = MultiModeItem('TestItem')
    p1 = ValueMode('modea', '1234')
    p2 = ValueMode('modeb', '4567')
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


def get_value_mode(enabled: bool, enable_on_value: bool, current_value=0) -> Tuple[Mock, ValueMode]:
    parent = Mock()
    parent.calculate_value = Mock()

    mode = ValueMode('mode1', current_value, enable_on_value=enable_on_value, enabled=enabled)
    mode.parent = parent
    return parent.calculate_value, mode


def test_only_on_change_1(parent_rule: DummyRule):
    calculate_value, mode = get_value_mode(enabled=False, enable_on_value=False)

    assert not mode.set_value(0, only_on_change=True)
    calculate_value.assert_not_called()


def test_only_on_change_2(parent_rule: DummyRule):
    calculate_value, mode = get_value_mode(enabled=True, enable_on_value=False)

    assert not mode.set_value(0, only_on_change=True)
    calculate_value.assert_not_called()


def test_only_on_change_3(parent_rule: DummyRule):
    calculate_value, mode = get_value_mode(enabled=False, enable_on_value=True)

    assert mode.set_value(0, only_on_change=True)
    calculate_value.assert_called_once()


def test_only_on_change_4(parent_rule: DummyRule):
    calculate_value, mode = get_value_mode(enabled=True, enable_on_value=True)

    assert not mode.set_value(0, only_on_change=True)
    calculate_value.assert_not_called()


@pytest.mark.parametrize('enabled', (True, False))
@pytest.mark.parametrize('enable_on_value', (True, False))
def test_only_on_change_diff_value(parent_rule: DummyRule, enabled, enable_on_value):

    calculate_value, mode = get_value_mode(enabled=enabled, enable_on_value=enable_on_value)

    assert mode.set_value(1, only_on_change=True)
    calculate_value.assert_called_once()


def test_calculate_lower_priority_value(parent_rule: DummyRule):
    p = MultiModeItem('TestItem', default_value=99)
    m1 = ValueMode('modea', '1234')
    m2 = ValueMode('modeb', '4567')
    p.add_mode(1, m1).add_mode(2, m2)

    assert p.value is None
    assert m1.calculate_lower_priority_value() is MISSING
    assert m2.calculate_lower_priority_value() == '1234'

    m1.set_value('asdf')
    assert m2.calculate_lower_priority_value() == 'asdf'


def test_auto_disable_1(parent_rule: DummyRule):
    p = MultiModeItem('TestItem')
    m1 = ValueMode('modea', 50)
    m2 = ValueMode('modeb', 60, auto_disable_func= lambda lower, o: lower > o)
    p.add_mode(1, m1).add_mode(2, m2)

    m1.set_value(50)
    assert p.value == 60

    m1.set_value(61)
    assert not m2.enabled
    assert p.value == 61

    m1.set_value(59)
    assert p.value == 59


def test_auto_disable_func(parent_rule: DummyRule):
    p = MultiModeItem('TestItem')
    m1 = ValueMode('modea', 50)
    m2 = ValueMode('modeb', 60, auto_disable_func=lambda low, s: low == 40)
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


def test_unknown(parent_rule: DummyRule):
    p = MultiModeItem('asdf')
    with pytest.raises(KeyError):
        p.get_mode('asdf')

    p.add_mode(1, BaseMode('mode'))
    with pytest.raises(KeyError):
        p.get_mode('asdf')


def test_remove(parent_rule: DummyRule):
    p = MultiModeItem('asdf')
    m1 = BaseMode('m1')
    m2 = BaseMode('m2')

    p.add_mode(0, m1)
    p.add_mode(1, m2)

    p.remove_mode('m1')

    assert p.all_modes() == [(1, m2)]


def test_overwrite(parent_rule: DummyRule):
    p = MultiModeItem('asdf')
    m1 = BaseMode('m1')
    m2 = BaseMode('m1')
    m3 = BaseMode('m3')

    p.add_mode(99, m1).add_mode(1, m2).add_mode(5, m3)

    assert p.all_modes() == [(1, m2), (5, m3)]


def test_order(parent_rule: DummyRule):
    p = MultiModeItem('asdf')
    m1 = BaseMode('m1')
    m2 = BaseMode('m2')
    m3 = BaseMode('m3')

    p.add_mode(99, m1)
    p.add_mode(1, m2)
    p.add_mode(5, m3)

    assert p.all_modes() == [(1, m2), (5, m3), (99, m1)]


def test_disable_no_default(parent_rule: DummyRule):

    # No default_value is set -> we don't send anything if all modes are disabled
    p1 = ValueMode('modea', '1234')
    p = MultiModeItem('TestItem').add_mode(1, p1)

    p1.set_enabled(True)
    assert p.value == '1234'
    p1.set_enabled(False)
    assert p.value == '1234'


def test_disable_with_default(parent_rule: DummyRule):

    # We have default_value set -> send it when all modes are disabled
    a1 = ValueMode('modea', '1234')
    a = MultiModeItem('TestItem', default_value=None).add_mode(1, a1)

    a1.set_enabled(True)
    assert a.value == '1234'
    a1.set_enabled(False)
    assert a.value is None
