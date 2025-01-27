from __future__ import annotations

import re
from base64 import b64decode, b64encode
from datetime import datetime
from typing import Any, Final, Literal

from fastnumbers import real
from pydantic import BaseModel
from typing_extensions import override
from whenever import Instant, LocalDateTime, OffsetDateTime, SystemDateTime, ZonedDateTime

from HABApp.core.const.const import PYTHON_311
from HABApp.core.types import HSB, RGB


class OpenHABDataType:
    @staticmethod
    def from_oh_str(state: str) -> Any:
        raise NotImplementedError()

    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        raise NotImplementedError()


class RestrictedOpenHABDataType(OpenHABDataType):
    @staticmethod
    def get_allowed_values() -> set[str]:
        raise NotImplementedError()


# ----------------------------------------------------------------------------------------------------------------------
# Primitive Types
# ----------------------------------------------------------------------------------------------------------------------

# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/RefreshType.java
class RefreshType(RestrictedOpenHABDataType):
    REFRESH: Final = 'REFRESH'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {RefreshType.REFRESH}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['REFRESH']:
        if state == 'REFRESH':
            return 'REFRESH'
        msg = f'Invalid state {state!r} for {RefreshType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value == 'REFRESH' or value is RefreshType:
            return 'REFRESH'
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/UnDefType.java
class UnDefType(RestrictedOpenHABDataType):
    UNDEF: Final = 'UNDEF'
    NULL: Final = 'NULL'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {UnDefType.UNDEF, UnDefType.NULL}

    @override
    @staticmethod
    def from_oh_str(state: str) -> None:
        if state in ('NULL', 'UNDEF'):
            return None
        msg = f'Invalid state {state!r} for {UnDefType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value is None or value is UnDefType:
            return 'NULL'
        return None


# ----------------------------------------------------------------------------------------------------------------------
# Library Types
# ----------------------------------------------------------------------------------------------------------------------


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/DateTimeType.java
class DateTimeType(OpenHABDataType):

    if PYTHON_311:
        @override
        @staticmethod
        def from_oh_str(state: str) -> datetime:
            # see implementation im map_values.py
            dt = datetime.fromisoformat(state)

            # all datetime objs from openHAB have a timezone set so we can't easily compare them
            # --> TypeError: can't compare offset-naive and offset-aware datetime
            dt = dt.astimezone(tz=None)      # Changes datetime object so it uses system timezone
            value = dt.replace(tzinfo=None)  # Removes timezone awareness
            return value  # noqa: RET504
    else:
        @override
        @staticmethod
        def from_oh_str(state: str) -> datetime:
            pos_dot = state.find('.')
            if (pos_plus := state.rfind('+')) == -1:
                pos_plus = state.rfind('-')
            if pos_plus - pos_dot > 6:
                state = state[:pos_dot + 7] + state[pos_plus:]
            dt = datetime.strptime(state, '%Y-%m-%dT%H:%M:%S.%f%z')

            # all datetime objs from openHAB have a timezone set so we can't easily compare them
            # --> TypeError: can't compare offset-naive and offset-aware datetime
            dt = dt.astimezone(tz=None)      # Changes datetime object so it uses system timezone
            value = dt.replace(tzinfo=None)  # Removes timezone awareness
            return value  # noqa: RET504

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if isinstance(value, datetime):
            # Add timezone (if not yet defined) to string, then remote anything below ms.
            # 2018-11-19T09:47:38.284000+0100 -> 2018-11-19T09:47:38.284+0100
            return value.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')

        # https://whenever.readthedocs.io/en/latest/overview.html#iso-8601
        if isinstance(value, (Instant, LocalDateTime, ZonedDateTime, OffsetDateTime, SystemDateTime)):
            return value.format_common_iso()

        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/DecimalType.java
class DecimalType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> int | float:
        return real(state)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if isinstance(value, (int, float)):
            return str(value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/HSBType.java
class HSBType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> HSB:
        h, s, b = state.split(',')
        return HSB(real(h), real(s), real(b))

    # noinspection PyProtectedMember
    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:

        if isinstance(value, HSB):
            h = value._hue
            s = value._saturation
            b = value._brightness
            return ','.join((
                str(h) if isinstance(h, int) else f'{h:.2f}',
                str(s) if isinstance(s, int) else f'{s:.2f}',
                str(b) if isinstance(b, int) else f'{b:.2f}',
            ))

        if isinstance(value, (tuple, list)) and len(value) == 3:
            return HSBType.to_oh_str(HSB(*value))

        if isinstance(value, RGB):
            return HSBType.to_oh_str(value.to_hsb())

        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/IncreaseDecreaseType.java
class IncreaseDecreaseType(RestrictedOpenHABDataType):
    INCREASE: Final = 'INCREASE'
    DECREASE: Final = 'DECREASE'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {IncreaseDecreaseType.INCREASE, IncreaseDecreaseType.DECREASE}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['INCREASE', 'DECREASE']:
        if state in ('INCREASE', 'DECREASE'):
            return state
        msg = f'Invalid state {state!r} for {IncreaseDecreaseType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('INCREASE', 'DECREASE'):
            return value
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/NextPreviousType.java
class NextPreviousType(RestrictedOpenHABDataType):
    NEXT: Final = 'NEXT'
    PREVIOUS: Final = 'PREVIOUS'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {NextPreviousType.NEXT, NextPreviousType.PREVIOUS}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['NEXT', 'PREVIOUS']:
        if state in ('NEXT', 'PREVIOUS'):
            return state
        msg = f'Invalid state {state!r} for {NextPreviousType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('NEXT', 'PREVIOUS'):
            return value
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/OnOffType.java
class OnOffType(RestrictedOpenHABDataType):
    ON: Final = 'ON'
    OFF: Final = 'OFF'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {OnOffType.ON, OnOffType.OFF}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['ON', 'OFF']:
        if state in ('ON', 'OFF'):
            return state
        msg = f'Invalid state {state!r} for {OnOffType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('ON', 'OFF'):
            return value
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/OnOffType.java
class OpenClosedType(RestrictedOpenHABDataType):
    OPEN: Final = 'OPEN'
    CLOSED: Final = 'CLOSED'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {OpenClosedType.OPEN, OpenClosedType.CLOSED}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['OPEN', 'CLOSED']:
        if state in ('OPEN', 'CLOSED'):
            return state
        msg = f'Invalid state {state!r} for {OpenClosedType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('OPEN', 'CLOSED'):
            return value
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PercentType.java
class PercentType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> int | float:
        value = real(state)
        if 0 <= value <= 100:
            return value
        msg = f'Invalid state {state!r} for {PercentType.__name__:s}'
        raise ValueError(msg)


    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if isinstance(value, (int, float)) and 0 <= value <= 100:
            return str(value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PlayPauseType.java
class PlayPauseType(OpenHABDataType):
    PLAY: Final = 'PLAY'
    PAUSE: Final = 'PAUSE'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {PlayPauseType.PLAY, PlayPauseType.PAUSE}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['PLAY', 'PAUSE']:
        if state in ('PLAY', 'PAUSE'):
            return state
        msg = f'Invalid state {state!r} for {PlayPauseType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('PLAY', 'PAUSE'):
            return value
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PointType.java
class PointType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> tuple[int | float, int | float, int | float | None]:
        values = state.split(',')
        match len(values):
            case 3:
                a, b, c = values
                return real(a), real(b), real(c)
            case 2:
                a, b = values
                return real(a), real(b), None

        msg = f'Invalid state {state!r} for {PointType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if not isinstance(value, (tuple, list)) or len(value) not in (2, 3):
            return None

        values = []
        for v in value:
            if v is None:
                continue
            if not isinstance(v, (int, float)):
                return None
            values.append(str(v))
        return ','.join(values)


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/QuantityType.java
class QuantityType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> tuple[int | float, str]:
        # Number:Dimensionless has no unit in the state
        if ' ' not in state:
            return real(state), ''

        value, unit = state.rsplit(' ', 1)
        return real(value), unit

    # We don't have the unit in HABApp that's why we send it the same way as the DecimalType
    to_oh_str = DecimalType.to_oh_str


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/RawType.java
class RawType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> tuple[str, bytes]:
        if not state.startswith('data:'):
            msg = f'Invalid state {state!r} for {RawType.__name__:s}'
            raise ValueError(msg)

        # The data is in this format
        # data:image/png;base64,iVBORw0KGgo...
        bin_type, data_str = state.split(';', 1)
        enc_str, bin_str = data_str.split(',', 1)

        if enc_str != 'base64':
            msg = f'Invalid encoding {enc_str!r} for {RawType.__name__:s}'
            raise ValueError(msg)

        return bin_type.removeprefix('data:'), b64decode(bin_str)

    @override
    @staticmethod
    def to_oh_str(value: bytes | tuple[bytes, str], image_type: str | None = None) -> str | None:
        if isinstance(value, tuple) and len(value) == 2:
            # This is a method call error, that's why we raise an error instead of returning None
            if image_type is not None:
                msg = 'image_type must be None if value is a tuple'
                raise ValueError(msg)

            value, image_type = value

        if not isinstance(value, bytes):
            return None
        if image_type is not None and not isinstance(image_type, str):
            return None

        # try to automatically find out what kind of file we have
        if image_type is None:
            if value.startswith(b'\xFF\xD8\xFF'):
                image_type = 'jpeg'
            elif value.startswith(b'\x89\x50\x4E\x47'):
                image_type = 'png'
            elif value.startswith(b'\x47\x49\x46\x38'):
                image_type = 'gif'

        if image_type not in ('jpeg', 'png', 'gif'):
            msg = f'Unknown image type: "{image_type}", File Signature: {value[:10].hex()}'
            raise ValueError(msg)

        return f'data:image/{image_type:s};base64,{b64encode(value).decode("ascii")}'


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/RewindFastforwardType.java
class RewindFastforwardType(RestrictedOpenHABDataType):
    REWIND: Final = 'REWIND'
    FASTFORWARD: Final = 'FASTFORWARD'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {RewindFastforwardType.REWIND, RewindFastforwardType.FASTFORWARD}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['REWIND', 'FASTFORWARD']:
        if state in ('REWIND', 'FASTFORWARD'):
            return state
        msg = f'Invalid state {state!r} for {RewindFastforwardType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('REWIND', 'FASTFORWARD'):
            return value
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StopMoveType.java
class StopMoveType(RestrictedOpenHABDataType):
    STOP: Final = 'STOP'
    MOVE: Final = 'MOVE'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {StopMoveType.STOP, StopMoveType.MOVE}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['STOP', 'MOVE']:
        if state in ('STOP', 'MOVE'):
            return state
        msg = f'Invalid state {state!r} for {StopMoveType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('STOP', 'MOVE'):
            return value
        return None


RE_SPLIT_STRINGLIST = re.compile(r'(?<!\\),')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StringListType.java
class StringListType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> tuple[str, ...]:
        if '\\' not in state:
            return tuple(state.split(','))
        return tuple(e.replace('\\,', ',') for e in RE_SPLIT_STRINGLIST.split(state))

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if isinstance(value, (tuple, list)):
            values = []
            for v in value:
                if not isinstance(v, str):
                    return None
                values.append(v.replace(',', '\\,'))
            return ','.join(values)
        if isinstance(value, str):
            return value.replace(',', '\\,')
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StringType.java
class StringType(OpenHABDataType):

    @override
    @staticmethod
    def from_oh_str(state: str) -> str:
        return state

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if isinstance(value, str):
            return value
        if isinstance(value, BaseModel):
            return value.model_dump_json()
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/UpDownType.java
class UpDownType(RestrictedOpenHABDataType):
    UP: Final = 'UP'
    DOWN: Final = 'DOWN'

    @override
    @staticmethod
    def get_allowed_values() -> set[str]:
        return {UpDownType.UP, UpDownType.DOWN}

    @override
    @staticmethod
    def from_oh_str(state: str) -> Literal['UP', 'DOWN']:
        if state in ('UP', 'DOWN'):
            return state
        msg = f'Invalid state {state!r} for {UpDownType.__name__:s}'
        raise ValueError(msg)

    @override
    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        if value in ('UP', 'DOWN'):
            return value
        return None


ALL_TYPES: Final[tuple[type[OpenHABDataType], ...]] = (
    RefreshType,
    UnDefType,
    DateTimeType,
    DecimalType,
    HSBType,
    IncreaseDecreaseType,
    NextPreviousType,
    OnOffType,
    OpenClosedType,
    PercentType,
    PlayPauseType,
    PointType,
    QuantityType,
    RawType,
    RewindFastforwardType,
    StopMoveType,
    StringListType,
    StringType,
    UpDownType,
)
