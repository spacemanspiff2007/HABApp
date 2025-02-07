from __future__ import annotations

from typing import Any

from HABApp.openhab.definitions.websockets.item_value_types import (
    DateTimeTypeModel,
    HSBTypeModel,
    PointTypeModel,
    RawTypeModel,
    StringListTypeModel,
)


def convert_to_oh_str(value: Any) -> str:
    if isinstance(value, (str, int, float)):
        return str(value)

    for cls in (HSBTypeModel, DateTimeTypeModel, PointTypeModel, RawTypeModel, StringListTypeModel):
        if (m := cls.from_value(value)) is not None:
            return m.value

    if isinstance(value, (list, tuple)):
        return StringListTypeModel.from_value([str(v) for v in value]).value

    if value is None:
        return 'NULL'

    raise ValueError()


def map_null_str(value: str) -> str | None:
    if value in ('NULL', 'UNDEF'):
        return None
    return value
