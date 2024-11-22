import typing

from tests.conftest import params

import HABApp
from HABApp import Parameter


if typing.TYPE_CHECKING:
    params = params


def test_simple_key_creation(params: HABApp.parameters.parameters) -> None:

    Parameter('file', 'key')
    assert params.get_parameter_file('file') == {'key': 'ToDo'}

    Parameter('file', 'key2')
    assert params.get_parameter_file('file') == {'key': 'ToDo', 'key2': 'ToDo'}


def test_structured_key_creation(params: HABApp.parameters.parameters) -> None:
    Parameter('file', 'key1', 'key1')
    Parameter('file', 'key1', 'key2')
    assert params.get_parameter_file('file') == {'key1': {'key1': 'ToDo', 'key2': 'ToDo'}}


def test_structured_default_value(params: HABApp.parameters.parameters) -> None:
    Parameter('file', 'key1', 'key1', default_value=123)
    Parameter('file', 'key1', 'key2', default_value=[1, 2, 3])
    assert params.get_parameter_file('file') == {'key1': {'key1': 123, 'key2': [1, 2, 3]}}


def test_lookup(params: HABApp.parameters.parameters) -> None:
    data = {'key1': {'key2': 'value2'}}
    params.set_parameter_file('file1', data)
    p = Parameter('file1', 'key1', 'key2')
    assert p == 'value2'

    data['key1']['key2'] = 3
    assert p == 3
