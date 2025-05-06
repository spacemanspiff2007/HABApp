import pytest
from whenever import SystemDateTime, patch_current_time

from HABApp.util import ExpiringCache


@pytest.fixture
def clock():
    with patch_current_time(SystemDateTime(2025, 1, 1, 12).to_instant(), keep_ticking=False) as t:
        yield t


@pytest.fixture
def cache(clock) -> ExpiringCache[str, str]:
    cache = ExpiringCache(30)
    cache['a'] = '1'
    clock.shift(nanoseconds=1)
    cache['b'] = '2'
    clock.shift(seconds=30)
    return cache


def test_reset(cache, clock) -> None:
    assert cache.is_expired('a')

    cache.reset('a')
    assert not cache.is_expired('a')

    clock.shift(seconds=30)
    assert not cache.is_expired('a')

    clock.shift(nanoseconds=1)
    assert cache.is_expired('a')


def test_iter(cache) -> None:
    assert cache.is_expired('a')
    assert not cache.is_expired('b')

    assert list(cache) == ['b']
    assert list(cache.keys()) == ['b']
    assert list(cache.values()) == ['2']
    assert list(cache.items()) == [('b', '2')]

    assert list(cache.keys('expired')) == ['a']
    assert list(cache.values('expired')) == ['1']
    assert list(cache.items('expired')) == [('a', '1')]

    assert list(cache.keys('all')) == ['a', 'b']
    assert list(cache.values('all')) == ['1', '2']
    assert list(cache.items('all')) == [('a', '1'), ('b', '2')]


def test_contains(cache) -> None:
    assert 'a' not in cache
    assert cache.in_cache('a')
    assert cache.is_expired('a')

    assert 'b' in cache
    assert cache.in_cache('b')
    assert not cache.is_expired('b')


def test_flush(cache) -> None:
    cache.flush().flush().flush()
    assert not cache.in_cache('a')
    assert 'b' in cache


def test_get(cache) -> None:

    assert cache.get('a') is None
    assert cache.get('a', 'asdf') == 'asdf'

    cache.set('a', '1')
    assert cache.get('a') == '1'

    assert cache.get('b') == '2'
    assert cache.get('b', 'asdf') == '2'


def test_getattr(cache, clock) -> None:

    assert cache['b'] == '2'

    with pytest.raises(KeyError) as e_missing:
        cache['key']

    cache['key'] = 'asdf'
    clock.shift(seconds=30, nanoseconds=1)

    with pytest.raises(KeyError) as e_expired:
        cache['key']

    assert str(e_missing.value) == str(e_expired.value)


def test_dict_interface(cache) -> None:
    assert len(cache) == 2
    del cache['a']
    assert len(cache) == 1

    with pytest.raises(KeyError):
        del cache['a']


def test_pop(cache) -> None:
    assert cache.pop('key', None) is None
    assert cache.pop('key', 'asdf') == 'asdf'

    with pytest.raises(KeyError):
        cache.pop('key')

    assert cache.in_cache('a')
    with pytest.raises(KeyError):
        assert cache.pop('a')
    assert not cache.in_cache('a')

    assert cache.in_cache('b')
    assert cache.pop('b') == '2'
    assert not cache.in_cache('b')


def test_set_expired(cache) -> None:
    assert not cache.is_expired('b')
    cache.set_expired('b')
    assert cache.is_expired('b')
