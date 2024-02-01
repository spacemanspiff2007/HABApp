import re

import pytest

import HABApp.util.rate_limiter.limits.fixed_window as fixed_window_module
import HABApp.util.rate_limiter.limits.leaky_bucket as leaky_bucket_module
import HABApp.util.rate_limiter.registry as registry_module
from HABApp.util.rate_limiter.limiter import (
    FixedWindowElasticExpiryLimit,
    FixedWindowElasticExpiryLimitInfo,
    LeakyBucketLimit,
    LeakyBucketLimitInfo,
    Limiter,
    parse_limit,
)
from HABApp.util.rate_limiter.parser import LIMIT_REGEX
from tests.helpers import MockedMonotonic


@pytest.fixture()
def time(monkeypatch) -> MockedMonotonic:
    m = MockedMonotonic()
    monkeypatch.setattr(fixed_window_module, 'monotonic', m.get_time)
    monkeypatch.setattr(leaky_bucket_module, 'monotonic', m.get_time)
    return m


@pytest.mark.parametrize(
    'unit,factor', [
        ('s', 1), ('sec', 1), ('second', 1),
        ('m', 60), ('min', 60), ('minute', 60),
        ('h', 3600), ('hour', 3600),
        ('day', 24 * 3600), ('month', 30 * 24 * 3600), ('year', 365 * 24 * 3600)
    ]
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


def test_parse_regex_all_units():
    m = re.search(r'\(([^)]+)\)s\?', LIMIT_REGEX.pattern)
    values = m.group(1)

    for unit in values.split('|'):
        parse_limit(f'1 in 3 {unit}')
        parse_limit(f'1 in 3 {unit}s')


def test_fixed_window(time):

    limit = FixedWindowElasticExpiryLimit(5, 3)
    assert str(limit) == '<FixedWindowElasticExpiryLimit hits=0/5 interval=3s window=0s>'
    for _ in range(10):
        assert limit.test_allow()

    assert limit.allow()
    assert str(limit) == '<FixedWindowElasticExpiryLimit hits=1/5 interval=3s window=3s>'

    for _ in range(4):
        assert limit.allow()

    assert str(limit) == '<FixedWindowElasticExpiryLimit hits=5/5 interval=3s window=3s>'

    # Limit is full, stop gets moved further
    time += 1
    assert not limit.allow()
    assert str(limit) == '<FixedWindowElasticExpiryLimit hits=5/5 interval=3s window=4s>'

    # move out of interval
    time += 3.1
    assert limit.allow()
    assert limit.hits == 1
    assert str(limit) == '<FixedWindowElasticExpiryLimit hits=1/5 interval=3s window=3s>'


def test_leaky_bucket(time):
    limit = LeakyBucketLimit(4, 2)
    assert str(limit) == '<LeakyBucketLimit hits=0/4 interval=2s drop_interval=0.5s>'
    for _ in range(10):
        assert limit.test_allow()

    assert limit.allow()
    assert limit.hits == 1

    assert limit.allow()
    assert limit.hits == 2

    assert limit.allow()
    assert limit.allow()
    assert not limit.allow()
    assert not limit.allow()
    assert limit.hits == 4

    time += 0.5
    assert limit.test_allow()
    assert limit.hits == 3

    time += 1.7
    assert limit.test_allow()
    assert limit.hits == 0

    assert limit.allow()
    assert limit.hits == 1

    time += 0.3
    assert limit.test_allow()
    assert limit.hits == 0

    time += 1
    assert limit.allow()
    time += 0.4999

    limit.test_allow()
    assert limit.hits == 1

    time += 0.0001
    limit.test_allow()
    assert limit.hits == 0


def test_window_test_allow(time):

    limit = FixedWindowElasticExpiryLimit(5, 3)
    limit.hits = 5
    limit.stop = 2.99999
    assert not limit.test_allow()

    # expiry when out of window
    time += 3
    assert limit.test_allow()
    assert not limit.hits


def test_limiter_add(time):
    limiter = Limiter('test')
    limiter.add_limit(3, 5).add_limit(3, 5).parse_limits('3 in 5s')
    assert len(limiter._limits) == 1

    with pytest.raises(ValueError) as e:
        limiter.add_limit(0, 5)
    assert str(e.value) == "Parameter allowed must be an int > 0, is 0 (<class 'int'>)"

    with pytest.raises(ValueError) as e:
        limiter.add_limit(1, 0.5)
    assert str(e.value) == "Parameter interval must be an int > 0, is 0.5 (<class 'float'>)"

    with pytest.raises(ValueError) as e:
        limiter.add_limit(3, 5, initial_hits=-1)
    assert str(e.value) == "Parameter hits must be an int >= 0, is -1 (<class 'int'>)"

    with pytest.raises(ValueError) as e:
        limiter.add_limit(3, 5, initial_hits=5)
    assert str(e.value) == "Parameter hits must be <= parameter allowed! 5 <= 3!"


def test_fixed_window_info(time):
    limit = FixedWindowElasticExpiryLimit(5, 3)
    Info = FixedWindowElasticExpiryLimitInfo

    assert limit.info() == Info(hits=0, skips=0, limit=5, time_remaining=3)

    limit.allow()
    assert limit.info() == Info(hits=1, skips=0, limit=5, time_remaining=3)
    limit.allow(4)
    assert limit.info() == Info(hits=5, skips=0, limit=5, time_remaining=3)
    limit.allow()
    assert limit.info() == Info(hits=5, skips=1, limit=5, time_remaining=3)

    time += 1
    assert limit.info() == Info(hits=5, skips=1, limit=5, time_remaining=2)

    time += 3
    assert limit.info() == Info(hits=0, skips=0, limit=5, time_remaining=3)

    assert not limit.test_allow(6)
    assert limit.info() == Info(hits=0, skips=0, limit=5, time_remaining=3)


def test_leaky_bucket_info(time):
    limit = LeakyBucketLimit(2, 2)
    Info = LeakyBucketLimitInfo

    assert limit.info() == Info(hits=0, skips=0, limit=2, time_remaining=1)


def test_registry(monkeypatch):
    monkeypatch.setattr(registry_module, '_LIMITERS', {})

    obj = registry_module.RateLimiter('Test')
    assert obj is registry_module.RateLimiter('TEST')
    assert obj is registry_module.RateLimiter('test')


def test_limiter(time):

    limiter = Limiter('Test')
    assert limiter.__repr__() == '<Limiter Test>'

    info = limiter.info()
    assert info.skips == 0

    with pytest.raises(ValueError):
        limiter.allow()

    limiter.add_limit(
        2, 1, algorithm='fixed_window_elastic_expiry').add_limit(2, 2, algorithm='fixed_window_elastic_expiry')

    assert limiter.allow()
    assert limiter.allow()
    time += 0.5
    assert not limiter.allow()

    time += 1
    assert not limiter.allow()

    assert limiter.info().skips == 2
    time += 2

    assert limiter.test_allow()
    assert limiter.info().skips == 0

    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()
    assert limiter.info().skips == 1

    time += 2
    assert limiter.allow()
    assert limiter.info().skips == 0
