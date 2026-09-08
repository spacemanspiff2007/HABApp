import typing

import pytest
from tests.conftest import params

from HABApp import Parameter
from HABApp.parameters.registry import PARAMS_PREFIX, PARAMS_SUFFIX, ParameterRegistry, get_user_name


if typing.TYPE_CHECKING:
    params = params


@pytest.mark.parametrize(('name', 'expected'), [
    ('params/file.yml', 'file'),
    ('PARAMS/file.YML', 'file'),
    ('Params/File.Yml', 'File'),
    ('file', 'file'),
    ('params/sub/file.yml', 'sub/file'),
])
def test_get_user_name(name: str, expected: str) -> None:
    assert get_user_name(name) == expected


def test_get_user_name_constants_case() -> None:
    # sanity check that the constants themselves are lower case as expected by the tests above
    assert PARAMS_PREFIX == PARAMS_PREFIX.lower()
    assert PARAMS_SUFFIX == PARAMS_SUFFIX.lower()


def test_simple_key_creation(params: ParameterRegistry) -> None:

    Parameter('file', 'key')
    assert params.get_value('file') == {'key': 'ToDo'}

    Parameter('file', 'key2')
    assert params.get_value('file') == {'key': 'ToDo', 'key2': 'ToDo'}

    Parameter('file2', 'key', default_value=123)
    assert params.get_value('file2') == {'key': 123}


def test_structured_key_creation(params: ParameterRegistry) -> None:
    Parameter('file', 'key1', 'key1')
    Parameter('file', 'key1', 'key2')
    assert params.get_value('file') == {'key1': {'key1': 'ToDo', 'key2': 'ToDo'}}


def test_structured_default_value(params: ParameterRegistry) -> None:
    Parameter('file', 'key1', 'key1', default_value=123)
    Parameter('file', 'key1', 'key2', default_value=[1, 2, 3])
    assert params.get_value('file') == {'key1': {'key1': 123, 'key2': [1, 2, 3]}}


def test_lookup(params: ParameterRegistry) -> None:
    data = {'key1': {'key2': 'value2'}}
    params._get_or_create_file('file1').data = data
    p = Parameter('file1', 'key1', 'key2')
    assert p == 'value2'

    data['key1']['key2'] = 3
    assert p == 3
