import pytest

from HABApp.openhab.definitions import DecimalType, UnDefType
from HABApp.openhab.items._converter import ValueToOh


def test_converter():
    a = ValueToOh('Asdf', UnDefType)
    b = a.add_type('Sdfg', DecimalType)

    assert a.to_oh_str(None) == UnDefType.NULL
    assert b.to_oh_str(None) == UnDefType.NULL

    with pytest.raises(ValueError):
        a.to_oh_str(1)
    assert b.to_oh_str(1) == '1'

    c = a.replace_type(UnDefType, DecimalType)
    assert c.to_oh_str(1) == '1'

    assert str(c) == 'ValueToOhAsdf(DecimalType)'
