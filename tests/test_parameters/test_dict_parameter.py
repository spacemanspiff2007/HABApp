import typing

import pytest
from tests.conftest import params

from HABApp import DictParameter
from HABApp.parameters.registry import ParameterRegistry


if typing.TYPE_CHECKING:
    params = params


def test_operators(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': {1: 2, 3: 4}}
    p = DictParameter('file', 'key')
    assert p == {1: 2, 3: 4}
    assert p != {1: 2, 3: 5}

    assert 1 in p
    assert 3 in p
    assert 2 not in p

    assert p[1] == 2
    assert p[3] == 4

    assert list(p) == [1, 3]


def test_funcs(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': {1: 2, 3: 4}}
    p = DictParameter('file', 'key')

    assert len(p) == 2

    assert list(p.keys()) == [1, 3]
    assert list(p.values()) == [2, 4]
    assert {k: v for k, v in p.items()} == {1: 2, 3: 4}

    assert p.get(5) is None
    assert p.get(5, 'asdf') == 'asdf'


def test_exception(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'key': 'value'}
    p = DictParameter('file', 'key')

    with pytest.raises(TypeError) as e:
        _ = p.value

    assert str(e.value) == 'Value "value" for DictParameter is not a dict! (<class \'str\'>)'
