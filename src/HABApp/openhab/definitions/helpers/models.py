from __future__ import annotations

from inspect import isclass
from types import UnionType
from typing import Annotated, Literal, Union, get_args, get_origin

from pydantic import BaseModel as _BaseModel


def get_literal_value(model: type[_BaseModel], field_name: str) -> str:
    if not isclass(model):
        raise TypeError()
    if not issubclass(model, _BaseModel):
        raise TypeError()

    if (field := model.model_fields.get(field_name)) is None:
        msg = f'Field with name {field_name:s} not found on {model!r:s}'
        raise ValueError(msg)

    annotation = field.annotation
    if (literal_type := get_origin(annotation)) is not Literal:
        msg = f'Expected {Literal!r}, got {literal_type!r}'
        raise TypeError(msg)

    literal_values = get_args(annotation)
    if len(literal_values) != 1:
        msg = f'Expected exactly one literal value for {literal_values!r}'
        raise ValueError(msg)

    value = literal_values[0]
    if not isinstance(value, str):
        raise TypeError()

    return value


def get_discriminator_values_from_union(union: type[_BaseModel], *,
                                        discriminator: str = 'type',
                                        allow_multiple: tuple[str, ...] = ()) -> list[str]:
    values: set[str] = set()

    type_hints = [union]

    while type_hints:
        type_hint = type_hints.pop(0)

        # Unpack Annotated
        if get_origin(type_hint) is Annotated:
            type_hints.append(get_args(type_hint)[0])
            continue

        # Unpack Union
        if get_origin(type_hint) in (Union, UnionType):
            type_hints.extend(get_args(type_hint))
            continue

        # It's a model -> get discriminator value
        if isclass(type_hint) and issubclass(type_hint, _BaseModel):
            if (value := get_literal_value(type_hint, discriminator)) in values and value not in allow_multiple:
                msg = f'Value {value:s} already in values'
                raise ValueError(msg)
            values.add(value)
            continue

        msg = f'Unknown type: {type_hint!r}'
        raise TypeError(msg)

    return sorted(values)
