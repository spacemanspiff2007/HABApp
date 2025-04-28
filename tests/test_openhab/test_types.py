from HABApp.openhab.types import RawType, StringList
from HABApp.openhab.types.quantity import QuantityFloat, QuantityInt


def test_raw_text() -> None:
    t = RawType.create('image/png', b'\x01' + b'\x00' * 1_000 + b'\x02')
    assert str(t) == 'RawType(type=png data=0100000000..0000000002 (1.0kiB))'

    b = b'\x01' + b'\x00' * 11_000 + b'\x02'
    t = RawType.create('image/png', b)
    assert str(t) == 'RawType(type=png data=0100000000..0000000002 (11kiB))'


def test_raw() -> None:

    b = b'\x01\x02'
    t = RawType('image/png', b)

    assert t.type == 'image/png'
    assert t.data == b

    assert t == RawType('image/png', b)
    assert t == b


def test_string_list() -> None:
    a = StringList(('a', 'b'))
    assert a == ('a', 'b')
    assert a != ('a', 1)

    assert a == ['a', 'b']
    assert a != ['a', 1]

    assert str(a) == "('a', 'b')"


def test_quantity() -> None:
    i = QuantityInt(1, 'asdf')
    assert i == 1
    assert i.unit == 'asdf'

    assert QuantityInt(1, 'asdf')._value_str() == '1 asdf'
    assert QuantityInt(1, '')._value_str() == '1'

    f = QuantityFloat(1.3, 'asdf')
    assert f == 1.3
    assert f.unit == 'asdf'

    assert QuantityFloat(1.3, 'asdf')._value_str() == '1.3 asdf'
    assert QuantityFloat(1.3, '')._value_str() == '1.3'
