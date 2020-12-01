import HABApp
import typing

from HABApp import Parameter
from tests.conftest import params

if typing.TYPE_CHECKING:
    params = params


def test_int_operators(params: HABApp.parameters.parameters):
    params.set_parameter_file('file', {'key': 5})
    p = Parameter('file', 'key')
    assert p == 5
    assert p != 6

    assert p < 6
    assert p <= 5
    assert p >= 5
    assert p > 4

    params.set_parameter_file('file', {'key': 15})
    assert not p < 6
    assert not p <= 5
    assert p >= 5
    assert p > 4


def test_float_operators(params: HABApp.parameters.parameters):
    params.set_parameter_file('file', {'key': 5.5})
    p = Parameter('file', 'key')

    assert p < 6
    assert not p <= 5
    assert p >= 5
    assert p > 4


def test_arithmetic(params: HABApp.parameters.parameters):
    params.set_parameter_file('file', {'key': 1})
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
