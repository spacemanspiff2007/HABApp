import typing

import pytest
from tests.conftest import params

import HABApp
from HABApp import DictParameter


if typing.TYPE_CHECKING:
    params = params


def test_operators(params: HABApp.parameters.parameters):
    params.set_parameter_file('file', {'key': {1: 2, 3: 4}})
    p = DictParameter('file', 'key')
    assert p == {1: 2, 3: 4}
    assert p != {1: 2, 3: 5}

    assert 1 in p
    assert 3 in p
    assert 2 not in p

    assert p[1] == 2
    assert p[3] == 4

    assert [k for k in p] == [1, 3]


def test_funcs(params: HABApp.parameters.parameters):
    params.set_parameter_file('file', {'key': {1: 2, 3: 4}})
    p = DictParameter('file', 'key')

    assert len(p) == 2

    assert list(p.keys()) == [1, 3]
    assert list(p.values()) == [2, 4]
    assert {k: v for k, v in p.items()} == {1: 2, 3: 4}

    assert p.get(5) is None
    assert p.get(5, 'asdf') == 'asdf'


def test_exception(params: HABApp.parameters.parameters):
    params.set_parameter_file('file', {'key': 'value'})
    p = DictParameter('file', 'key')

    with pytest.raises(ValueError) as e:
        _ = p.value

    assert str(e.value) == 'Value "value" for DictParameter is not a dict! (<class \'str\'>)'
