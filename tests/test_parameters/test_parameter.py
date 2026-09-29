import typing

from tests.conftest import params

from HABApp import Parameter
from HABApp.parameters.registry import ParameterRegistry


if typing.TYPE_CHECKING:
    params = params


def test_int_operators(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': 5}
    p = Parameter('file', 'key')
    assert p == 5
    assert p != 6

    assert p < 6
    assert p <= 5
    assert p >= 5
    assert p > 4

    params._get_or_create_file('file').data = {'key': 15}
    assert not p < 6
    assert not p <= 5
    assert p >= 5
    assert p > 4


def test_float_operators(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': 5.5}
    p = Parameter('file', 'key')

    assert p < 6
    assert not p <= 5
    assert p >= 5
    assert p > 4


def test_arithmetic(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': 1}
    p = Parameter('file', 'key')

    assert int(p) == 1
    assert p + 1 == 2
    assert p - 1 == 0
    assert p * 3 == 3
    assert p / 2 == 0.5
    assert p // 2 == 0
    assert p << 1 == 2
    assert p >> 1 == 0
    assert p | 2 == 3
    assert p & 2 == 0
