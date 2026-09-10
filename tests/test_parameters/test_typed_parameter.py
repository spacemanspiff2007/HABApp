import typing

import pytest
from tests.conftest import params

from HABApp.parameters import FloatParameter, IntParameter, NumberParameter, Parameter, StrParameter
from HABApp.parameters.registry import ParameterRegistry


if typing.TYPE_CHECKING:
    params = params


def test_str_parameter(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': 'value'}
    p = StrParameter('file', 'key')
    assert p.value == 'value'

    params._get_or_create_file('file').data = {'key': 5}
    with pytest.raises(TypeError):
        _ = p.value


def test_int_parameter(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': 5}
    p = IntParameter('file', 'key')
    assert p.value == 5

    params._get_or_create_file('file').data = {'key': 5.5}
    with pytest.raises(TypeError):
        _ = p.value


def test_float_parameter(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': 5.5}
    p = FloatParameter('file', 'key')
    assert p.value == 5.5
    assert isinstance(p.value, float)

    # int values are not accepted, must be a float
    params._get_or_create_file('file').data = {'key': 5}
    with pytest.raises(TypeError):
        _ = p.value

    params._get_or_create_file('file').data = {'key': 'nope'}
    with pytest.raises(TypeError):
        _ = p.value


def test_number_parameter(params: ParameterRegistry) -> None:
    p = NumberParameter('file', 'key')

    params._get_or_create_file('file').data = {'key': 5}
    assert p.value == 5
    assert isinstance(p.value, int)

    params._get_or_create_file('file').data = {'key': 5.5}
    assert p.value == 5.5
    assert isinstance(p.value, float)

    params._get_or_create_file('file').data = {'key': 'nope'}
    with pytest.raises(TypeError):
        _ = p.value


def test_parameter_default_type(params: ParameterRegistry) -> None:
    # Parameter without an explicit type behaves as before (no type check)
    params._get_or_create_file('file').data = {'key': 'value'}
    p = Parameter('file', 'key')
    assert p.value == 'value'
