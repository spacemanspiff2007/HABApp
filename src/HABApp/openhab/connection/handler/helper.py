from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from whenever import Instant, LocalDateTime, OffsetDateTime, SystemDateTime, ZonedDateTime

from HABApp.core.types import HSB, RGB


def convert_to_oh_type(obj: Any, scientific_floats: bool = False) -> str:
    if isinstance(obj, (str, int, bool)):
        return str(obj)

    if isinstance(obj, float):
        if scientific_floats:
            return str(obj)

        v = str(obj)
        if 'e-' not in v:
            return v

        v = f'{obj:.{int(v.split("e-", maxsplit=1)[1]) + 6}f}'
        return v.rstrip('0')

    if isinstance(obj, datetime):
        # Add timezone (if not yet defined) to string, then remote anything below ms.
        # 2018-11-19T09:47:38.284000+0100 -> 2018-11-19T09:47:38.284+0100
        return obj.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')

    if obj is None:
        return 'NULL'

    if isinstance(obj, RGB):
        obj = obj.to_hsb()

    if isinstance(obj, HSB):
        # noinspection PyProtectedMember
        return f'{obj._hue:.2f},{obj._saturation:.2f},{obj._brightness:.2f}'

    # https://whenever.readthedocs.io/en/latest/overview.html#iso-8601
    if isinstance(obj, (Instant, LocalDateTime, ZonedDateTime, OffsetDateTime, SystemDateTime)):
        return obj.format_common_iso()

    if isinstance(obj, (list, tuple, set, frozenset)):
        return ','.join(convert_to_oh_type(x, scientific_floats=scientific_floats) for x in obj)

    if isinstance(obj, BaseModel):
        return obj.model_dump_json()

    raise ValueError()


def map_null_str(value: str) -> str | None:
    if value in ('NULL', 'UNDEF'):
        return None
    return value
