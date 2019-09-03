from unittest.mock import MagicMock

from HABApp.util import MultiValue


def test_same_priority():

    on_change_func = MagicMock()

    p = MultiValue(on_value_change=on_change_func)
    a1 = p.get_create_value(0, '1234')
    a2 = p.get_create_value(0, '1234')

    a2.set_value(1)
    assert p.value == 1
    on_change_func.assert_called_once_with(1)

    a1.set_value(2)
    assert p.value == 2
    on_change_func.assert_called_with(2)


def test_diff_prio():

    on_change_func = MagicMock()

    p = MultiValue(on_value_change=on_change_func)
    p1 = p.get_create_value(1, '1234')
    p2 = p.get_create_value(2, '4567')

    p1.set_value(5)
    assert p.value == '4567'
    on_change_func.assert_called_with('4567')

    p2.set_enabled(False)
    assert p.value == 5
    on_change_func.assert_called_with(5)

    p2.set_enabled(True)
    assert p.value == '4567'
    on_change_func.assert_called_with('4567')

    p2.set_enabled(False)
    p2.set_value(8888)
    assert p.value == 8888
    on_change_func.assert_called_with(8888)
