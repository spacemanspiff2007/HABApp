from __future__ import annotations

from typing import Any

from HABApp.openhab.definitions import (
    DateTimeType,
    HSBType,
    PointType,
    RawType,
    RefreshType,
    StringListType,
    StringType,
    UnDefType,
)


def convert_to_oh_type(value: Any) -> str:
    if isinstance(value, (str, int, float)):
        return str(value)

    if isinstance(value, (list, tuple)):
        # data types that accept lists and tuples need to be handled separately
        # oder matters!
        for t in (StringListType, PointType, HSBType, RawType):
            if (send := t.to_oh_str(value)) is not None:
                return send

    for t in (HSBType, DateTimeType, RefreshType, UnDefType, StringType, RawType):
        if (send := t.to_oh_str(value)) is not None:
            return send

    raise ValueError()


def map_null_str(value: str) -> str | None:
    if value in ('NULL', 'UNDEF'):
        return None
    return value
