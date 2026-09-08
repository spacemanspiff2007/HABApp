import typing

import pytest
from pydantic import BaseModel, ValidationError
from tests.conftest import params

from HABApp import BaseModelParameter
from HABApp.parameters.registry import ParameterRegistry


if typing.TYPE_CHECKING:
    params = params


class SubModel(BaseModel):
    threshold: int
    name: str = 'default'


def test_value_is_validated_model_instance(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'sub': {'threshold': 5, 'name': 'abc'}}

    p = BaseModelParameter('file', 'sub', model=SubModel)
    value = p.value

    assert isinstance(value, SubModel)
    assert value.threshold == 5
    assert value.name == 'abc'


def test_value_uses_model_defaults(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'sub': {'threshold': 5}}

    p = BaseModelParameter('file', 'sub', model=SubModel)
    assert p.value.name == 'default'


def test_value_is_always_freshly_validated(params: ParameterRegistry) -> None:
    data = {'sub': {'threshold': 5, 'name': 'abc'}}
    params._get_or_create_file('file').data = data

    p = BaseModelParameter('file', 'sub', model=SubModel)
    assert p.value.threshold == 5

    data['sub']['threshold'] = 10
    assert p.value.threshold == 10


def test_invalid_value_raises(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'sub': {'name': 'abc'}}

    p = BaseModelParameter('file', 'sub', model=SubModel)
    with pytest.raises(ValidationError):
        _ = p.value


def test_repr(params: ParameterRegistry) -> None:
    params._get_or_create_file('file').data = {'sub': {'threshold': 5, 'name': 'abc'}}

    p = BaseModelParameter('file', 'sub', model=SubModel)
    assert repr(p) == "<BaseModelParameter file: file, keys: ('sub',), model: SubModel>"
