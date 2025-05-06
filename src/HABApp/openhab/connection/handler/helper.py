from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from whenever import Instant, OffsetDateTime, PlainDateTime, SystemDateTime, ZonedDateTime

from HABApp.core.types import HSB, RGB
from HABApp.openhab.definitions.websockets.item_value_types import RawTypeModel


def convert_to_oh_str(obj: Any) -> str:
    if isinstance(obj, (str, int, float)):
        return str(obj)

    if isinstance(obj, datetime):
        # Add timezone (if not yet defined) to string, then remote anything below ms.
        # 2018-11-19T09:47:38.284000+0100 -> 2018-11-19T09:47:38.284+0100
        return obj.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')

    if obj is None:
        return 'NULL'

    if isinstance(obj, RGB):
        obj = obj.to_hsb()

    if isinstance(obj, (list, tuple, set, frozenset)):
        return ','.join(convert_to_oh_str(x) for x in obj)

    if isinstance(obj, BaseModel):
        return obj.model_dump_json()

    if isinstance(obj, HSB):
        # noinspection PyProtectedMember
        return f'{obj._hue:.2f},{obj._saturation:.2f},{obj._brightness:.2f}'

    if isinstance(obj, bytes):
        return RawTypeModel.from_value(obj).value

    # https://whenever.readthedocs.io/en/latest/overview.html#iso-8601
    if isinstance(obj, (Instant, PlainDateTime, ZonedDateTime, OffsetDateTime, SystemDateTime)):
        return obj.format_common_iso()

    raise ValueError()


def map_null_str(value: str) -> str | None:
    if value in ('NULL', 'UNDEF'):
        return None
    return value
