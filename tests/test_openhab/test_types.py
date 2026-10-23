from statistics import mean

import pytest

from HABApp.core.const import MISSING
from HABApp.openhab.types import EventSourceStr, RawType, StringList
from HABApp.openhab.types.event_source import EventSourceComponent
from HABApp.openhab.types.quantity import QuantityFloat, QuantityInt


def test_raw_text() -> None:
    t = RawType.create('image/png', b'\x01' + b'\x00' * 1_000 + b'\x02')
    assert str(t) == 'RawType(type=png data=0100000000..0000000002 (1.0kiB))'

    b = b'\x01' + b'\x00' * 11_000 + b'\x02'
    t = RawType.create('image/png', b)
    assert str(t) == 'RawType(type=png data=0100000000..0000000002 (11kiB))'


def test_raw_type() -> None:
    t = RawType.create('image/svg+xml', b'')
    assert t.type == 'svg+xml'

    t = RawType.create('image/vnd.clip', b'')
    assert t.type == 'vnd.clip'


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

    # test operator
    e = i * QuantityInt(20_000, 'unit')
    assert type(e) is int
    e = f * QuantityFloat(20.0, 'unit')
    assert type(e) is float

    # Test conversion
    # literals are 0..100 constants, this saves us the type check
    assert int(i) is 1  # noqa: F632

    # Test utility function which should work out of the box
    result = mean([QuantityInt(10_000, 'u1'), QuantityInt(20_000, 'u2')])
    assert result == 15_000
    assert type(result) is int
    result = mean([QuantityFloat(1.0, 'u1'), QuantityFloat(2.0, 'u2')])
    assert result == 1.5
    assert type(result) is float


def test_event_source_type() -> None:
    with pytest.raises(TypeError):
        EventSourceStr(1)


def test_event_source_empty() -> None:
    s = EventSourceStr('')
    assert s.components == ()
    assert s.origin is None
    assert s.bundle is None
    assert s.actor is None
    assert s.is_delegated is False


def test_event_source_plain_bundle() -> None:
    s = EventSourceStr('org.openhab.core.automation')
    assert s.components == (EventSourceComponent('org.openhab.core.automation', None),)
    assert s.origin == EventSourceComponent('org.openhab.core.automation', None)
    assert s.bundle == 'org.openhab.core.automation'
    assert s.actor is None
    assert s.is_delegated is False


def test_event_source_bundle_with_actor() -> None:
    s = EventSourceStr('org.openhab.binding.mqtt$mqtt:thing:mything:mychannel')
    assert s.components == (EventSourceComponent('org.openhab.binding.mqtt', 'mqtt:thing:mything:mychannel'),)
    assert s.bundle == 'org.openhab.binding.mqtt'
    assert s.actor == 'mqtt:thing:mything:mychannel'
    assert s.is_delegated is False


def test_event_source_delegated() -> None:
    value = 'org.openhab.ui.basic$default:03=>org.openhab.core.io.rest'
    s = EventSourceStr(value)

    assert s.is_delegated is True
    assert s.components == (
        EventSourceComponent('org.openhab.ui.basic', 'default:03'),
        EventSourceComponent('org.openhab.core.io.rest', None),
    )
    assert s.origin == EventSourceComponent('org.openhab.ui.basic', 'default:03')
    assert s.bundle == 'org.openhab.ui.basic'
    assert s.actor == 'default:03'


def test_event_source_long_delegation_chain() -> None:
    value = (
        'org.openhab.ui.basic$default:03=>org.openhab.android$my-phone=>'
        'org.openhab.io.openhabcloud$user@gmail.com=>org.openhab.core.io.rest'
    )
    s = EventSourceStr(value)

    assert s.components == (
        EventSourceComponent('org.openhab.ui.basic', 'default:03'),
        EventSourceComponent('org.openhab.android', 'my-phone'),
        EventSourceComponent('org.openhab.io.openhabcloud', 'user@gmail.com'),
        EventSourceComponent('org.openhab.core.io.rest', None),
    )


def test_event_source_actor_with_dollar() -> None:
    # Actor names may contain the "$" separator again - only the bundle name may not
    s = EventSourceStr('org.openhab.example$actor$with$dollars')
    assert s.bundle == 'org.openhab.example'
    assert s.actor == 'actor$with$dollars'


def test_event_source_str_repr() -> None:
    assert str(EventSourceComponent('bundle', None)) == 'bundle'
    assert str(EventSourceComponent('bundle', 'actor')) == 'bundle$actor'


def test_event_source_is_str() -> None:
    value = 'org.openhab.core.automation'
    s = EventSourceStr(value)
    assert s == value
    assert isinstance(s, str)


def test_event_source_components_are_cached() -> None:
    s = EventSourceStr('org.openhab.core.automation')
    # access twice and make sure the same (cached) tuple object is returned
    assert s.components is s.components


def test_event_source_of_habapp() -> None:
    # HABApp uses a fixed, "." based convention ("HABApp.<actor>") instead of the regular "$" separator.
    # It's parsed transparently, i.e. there is no special property/method for it - bundle/actor just work.
    s = EventSourceStr('HABApp.my_rule')
    assert s.bundle == 'HABApp'
    assert s.actor == 'my_rule'
    assert s.components == (EventSourceComponent('HABApp', 'my_rule'),)
    assert s.is_delegated is False


def test_event_source_habapp_without_actor() -> None:
    s = EventSourceStr('HABApp.')
    assert s.bundle == 'HABApp'
    assert s.actor is None


def test_event_source_habapp_plain() -> None:
    # Just "HABApp" without the "." is parsed like any other, actor-less bundle
    s = EventSourceStr('HABApp')
    assert s.bundle == 'HABApp'
    assert s.actor is None


def test_event_source_habapp_dollar_separator() -> None:
    # The regular "$" separator also works for the "HABApp" bundle
    s = EventSourceStr('HABApp$my_rule')
    assert s.bundle == 'HABApp'
    assert s.actor == 'my_rule'


def test_event_source_habapp_lookalike_bundle_not_special_cased() -> None:
    # Only the exact "HABApp." prefix is special-cased, bundles that merely start with "HABApp" are not
    s = EventSourceStr('HABAppFoo.bar')
    assert s.bundle == 'HABAppFoo.bar'
    assert s.actor is None


def test_event_source_habapp_delegated() -> None:
    # bundle/actor only look at the origin (first) component of the source
    s = EventSourceStr('HABApp.my_rule=>org.openhab.core.io.rest')
    assert s.bundle == 'HABApp'
    assert s.actor == 'my_rule'
    assert s.is_delegated is True


def test_event_source_bundle_actor_cached_independently_of_components() -> None:
    s = EventSourceStr('org.openhab.core.automation')
    assert s._components is MISSING

    # bundle/actor are cached independently of (and without building) the full components tuple
    assert s.bundle == 'org.openhab.core.automation'
    assert s.actor is None
    assert s._components is MISSING

    # components is a separate, independently lazy cache
    assert s.components == (EventSourceComponent('org.openhab.core.automation', None),)
    assert s._components is not MISSING
    assert s.components is s.components


def test_event_source_origin_matches_bundle_actor() -> None:
    s = EventSourceStr('org.openhab.binding.mqtt$mqtt:thing:mything:mychannel')
    assert s.origin == EventSourceComponent('org.openhab.binding.mqtt', 'mqtt:thing:mything:mychannel')
    assert s.origin == s.components[0]
