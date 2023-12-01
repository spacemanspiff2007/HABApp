import pytest

import HABApp.util.rate_limiter.limiter as limiter_module
import HABApp.util.rate_limiter.rate_limit as rate_limit_module
import HABApp.util.rate_limiter.registry as registry_module
from HABApp.util.rate_limiter.limiter import Limiter, RateLimit, parse_limit


@pytest.mark.parametrize(
    'unit,factor', (
        ('s', 1), ('sec', 1), ('second', 1),
        ('m', 60), ('min', 60), ('minute', 60),
        ('h', 3600), ('hour', 3600),
        ('day', 24 * 3600), ('month', 30 * 24 * 3600), ('year', 365 * 24 * 3600)
    )
)
def test_parse(unit: str, factor: int):
    assert parse_limit(f'  1   per   {unit}  ') == (1, factor)
    assert parse_limit(f'  1   /   {unit}  ') == (1, factor)
    assert parse_limit(f'3 per {unit}') == (3, factor)
    assert parse_limit(f'3 in {unit}') == (3, factor)

    for ctr in (1, 12, 375, 5533):
        assert parse_limit(f'{ctr:d} in 5{unit}') == (ctr, 5 * factor)
        assert parse_limit(f'{ctr:d} in 5{unit}s') == (ctr, 5 * factor)

    with pytest.raises(ValueError) as e:
        parse_limit('asdf')
    assert str(e.value) == 'Invalid limit string: "asdf"'


def test_window(monkeypatch):
    time = 0
    monkeypatch.setattr(rate_limit_module, 'monotonic', lambda: time)

    limit = RateLimit(5, 3)
    assert str(limit) == '<RateLimit hits=0/5 expiry=3s window=0s>'
    assert limit.test_allow()

    assert limit.allow()
    assert str(limit) == '<RateLimit hits=1/5 expiry=3s window=3s>'

    for _ in range(4):
        assert limit.allow()

    assert str(limit) == '<RateLimit hits=5/5 expiry=3s window=3s>'

    # Limit is full, stop gets moved further
    time = 1
    assert not limit.allow()
    assert str(limit) == '<RateLimit hits=5/5 expiry=3s window=4s>'

    # move out of interval
    time = 4.1
    assert limit.allow()
    assert limit.hits == 1
    assert str(limit) == '<RateLimit hits=1/5 expiry=3s window=3s>'


def test_window_test_allow(monkeypatch):
    time = 0
    monkeypatch.setattr(rate_limit_module, 'monotonic', lambda: time)

    limit = RateLimit(5, 3)
    limit.hits = 5
    limit.stop = 2.99999
    assert not limit.test_allow()

    # expiry when out of window
    time = 3
    assert limit.test_allow()
    assert not limit.hits


def test_limiter_add(monkeypatch):
    limiter = Limiter('test')
    limiter.add_limit(3, 5).add_limit(3, 5).parse_limits('3 in 5s')
    assert len(limiter._limits) == 1


def test_limiter_info(monkeypatch):
    time = 0
    monkeypatch.setattr(rate_limit_module, 'monotonic', lambda: time)
    monkeypatch.setattr(limiter_module, 'monotonic', lambda: time)

    limiter = Limiter('test')

    info = limiter.info()
    assert info.time_remaining == 0
    assert info.skipped == 0

    with pytest.raises(ValueError):
        limiter.allow()

    with pytest.raises(ValueError):
        limiter.test_allow()

    limiter.add_limit(3, 3)

    info = limiter.info()
    assert info.time_remaining == 0
    assert info.skipped == 0

    w_info = info.limits[0]
    assert w_info.limit == 3
    assert w_info.skips == 0
    assert w_info.time_remaining == 3
    assert w_info.hits == 0

    limiter.allow()
    time = 2
    limiter.allow()

    info = limiter.info()
    assert info.time_remaining == 1
    assert info.skipped == 0

    w_info = info.limits[0]
    assert w_info.limit == 3
    assert w_info.skips == 0
    assert w_info.time_remaining == 1
    assert w_info.hits == 2

    # add a longer limiter - this one should now define the time_remaining
    limiter.add_limit(4, 5)
    limiter.allow()

    info = limiter.info()
    assert info.time_remaining == 5
    assert info.skipped == 0

    w_info = info.limits[0]
    assert w_info.limit == 3
    assert w_info.skips == 0
    assert w_info.time_remaining == 1
    assert w_info.hits == 3

    w_info = info.limits[1]
    assert w_info.limit == 4
    assert w_info.skips == 0
    assert w_info.time_remaining == 5
    assert w_info.hits == 1

    time += 5.0001

    info = limiter.info()
    assert info.time_remaining == 0

    w_info = info.limits[0]
    assert w_info.limit == 3
    assert w_info.skips == 0
    assert w_info.time_remaining == 0
    assert w_info.hits == 3

    w_info = info.limits[1]
    assert w_info.limit == 4
    assert w_info.skips == 0
    assert w_info.time_remaining == 0
    assert w_info.hits == 1


def test_registry(monkeypatch):
    monkeypatch.setattr(registry_module, '_LIMITERS', {})

    obj = registry_module.RateLimiter('test')
    assert obj is registry_module.RateLimiter('TEST')
