from __future__ import annotations

from datetime import datetime
from typing import Any

from HABApp.core.items import BaseValueItem
from HABApp.core.types import RGB, HSB


def convert_to_oh_type(obj: Any) -> str:
    if isinstance(obj, (str, int, bool)):
        return str(obj)

    if isinstance(obj, float):
        v = str(obj)
        if 'e-' not in v:
            return v

        v = f'{obj:.{int(v.split("e-", maxsplit=1)[1]) + 6}f}'
        return v.rstrip('0')

    if isinstance(obj, datetime):
        # Add timezone (if not yet defined) to string, then remote anything below ms.
        # 2018-11-19T09:47:38.284000+0100 -> 2018-11-19T09:47:38.284+0100
        out = obj.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        return out

    if isinstance(obj, (set, list, tuple, frozenset)):
        return ','.join(map(str, obj))

    if obj is None:
        return 'NULL'

    if isinstance(obj, RGB):
        obj = obj.to_hsb()

    if isinstance(obj, HSB):
        # noinspection PyProtectedMember
        return f'{obj._hue:.2f},{obj._saturation:.2f},{obj._brightness:.2f}'

    if isinstance(obj, BaseValueItem):
        raise ValueError()

    return str(obj)


def map_null_str(value: str) -> str | None:
    if value == 'NULL' or value == 'UNDEF':
        return None
    return value
