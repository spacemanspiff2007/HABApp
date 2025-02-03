from HABApp.openhab.types import RawType


def test_raw_text():
    t = RawType.create('image/png', b'\x01' + b'\x00' * 1_000 + b'\x02')
    assert str(t) == 'RawType(type=png data=0100000000..0000000002 (1.0kiB))'

    b = b'\x01' + b'\x00' * 11_000 + b'\x02'
    t = RawType.create('image/png', b)
    assert str(t) == 'RawType(type=png data=0100000000..0000000002 (11kiB))'


def test_raw():

    b = b'\x01\x02'
    t = RawType('image/png', b)

    assert t.type == 'image/png'
    assert t.data == b

    assert t == RawType('image/png', b)
    assert t == b
