import re
from base64 import b64decode, b64encode
from datetime import datetime
from typing import Annotated, Any, Literal

from fastnumbers import float as fast_float
from fastnumbers import real, try_int, try_real
from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, Field, TypeAdapter
from typing_extensions import Self, override
from whenever import Instant, LocalDateTime, OffsetDateTime, SystemDateTime, ZonedDateTime

from HABApp.core.types import HSB, RGB, Point
from HABApp.openhab.types import RawType, StringList
from HABApp.openhab.types.quantity import QuantityFloat, QuantityInt


class BaseModel(_BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, validate_default=True, validate_assignment=True)


class ItemValueBase(BaseModel):
    def get_value(self) -> Any:
        raise NotImplementedError()

    @staticmethod
    def get_value_from_state(state: str) -> Any:
        raise NotImplementedError()

    @classmethod
    def from_value(cls, value: Any) -> Self | None:
        raise NotImplementedError()


# ----------------------------------------------------------------------------------------------------------------------
# Primitive Types
# ----------------------------------------------------------------------------------------------------------------------

# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/RefreshType.java
class RefreshTypeModel(ItemValueBase):
    type: Literal['Refresh']
    value: Literal['REFRESH']

    @override
    def get_value(self) -> Literal['REFRESH']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: Literal['REFRESH'] | None) -> Self | None:
        if value in ('REFRESH', ):
            return cls(type='Refresh', value='REFRESH')
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/UnDefType.java
class UnDefTypeModel(ItemValueBase):
    type: Literal['UnDef']
    value: Literal['NULL', 'UNDEF']

    @override
    def get_value(self) -> None:
        return None

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: None = None) -> Self | None:
        if value is None:
            return cls(type='UnDef', value='NULL')
        return None


# ----------------------------------------------------------------------------------------------------------------------
# Library Types
# ----------------------------------------------------------------------------------------------------------------------

# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/DateTimeType.java
class DateTimeTypeModel(ItemValueBase):
    type: Literal['DateTime']
    value: str = Field(pattern=r'^\d{4}\-\d\d\-\d\dT\d\d:\d\d:\d\d')

    @override
    def get_value(self) -> datetime:
        value = self.value
        # Currently colon is not supported
        # https://github.com/ariebovenberg/whenever/issues/204
        return OffsetDateTime.parse_common_iso(f'{value[:-2]:s}:{value[-2:]:s}').local().py_datetime()

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> datetime:
        # noinspection PyTypeChecker
        # Is not strict, that's why we can pass a string
        return DateTimeTypeModel(type='DateTime', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: datetime | Instant | LocalDateTime |
                               ZonedDateTime | OffsetDateTime | SystemDateTime) -> Self | None:
        if isinstance(value, datetime):
            return cls(type='DateTime', value=value.isoformat())

        # https://whenever.readthedocs.io/en/latest/overview.html#iso-8601
        if isinstance(value, (Instant, LocalDateTime, ZonedDateTime, OffsetDateTime, SystemDateTime)):
            return cls(type='DateTime', value=value.format_common_iso())

        if isinstance(value, str):
            # try parsing through whenever types and datetime
            for parse in (Instant.parse_common_iso, LocalDateTime.parse_common_iso, ZonedDateTime.parse_common_iso,
                          OffsetDateTime.parse_common_iso, SystemDateTime.parse_common_iso, datetime.fromisoformat):
                try:
                    v = parse(value)
                except ValueError:  # noqa: PERF203
                    pass
                else:
                    return cls.from_value(v)

        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/DecimalType.java
class DecimalTypeModel(ItemValueBase):
    type: Literal['Decimal']
    value: str

    @override
    def get_value(self) -> float:
        return real(self.value)

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> float:
        return DecimalTypeModel(type='Decimal', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: float) -> Self | None:
        if isinstance(value, (int, float)):
            return cls(type='Decimal', value=str(value))
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/HSBType.java
class HSBTypeModel(ItemValueBase):
    type: Literal['HSB']
    value: str = Field(pattern=r'^\d+(\.\d+)?,\d+(\.\d+)?,\d+(\.\d+)?$')

    @override
    def get_value(self) -> HSB:
        h, s, b = self.value.split(',')
        return HSB(real(h), real(s), real(b))

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> HSB:
        return HSBTypeModel(type='HSB', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: HSB | RGB) -> Self | None:
        if isinstance(value, HSB):
            h = value._hue
            s = value._saturation
            b = value._brightness
            out = ','.join((
                str(h) if isinstance(h, int) else f'{h:.2f}',
                str(s) if isinstance(s, int) else f'{s:.2f}',
                str(b) if isinstance(b, int) else f'{b:.2f}',
            ))
            return cls(type='HSB', value=out)

        if isinstance(value, RGB):
            return cls.from_value(value.to_hsb())

        if isinstance(value, (tuple, list)) and len(value) == 3:
            if len(value) != 3 or not all(isinstance(v, (int, float)) for v in value):
                return None
            return cls(
                type='HSB',
                value=','.join(str(v) if isinstance(v, int) else f'{v:.2f}' for v in value)
            )

        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/IncreaseDecreaseType.java
class IncreaseDecreaseTypeModel(ItemValueBase):
    type: Literal['IncreaseDecrease']
    value: Literal['INCREASE', 'DECREASE']

    @override
    def get_value(self) -> Literal['INCREASE', 'DECREASE']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('INCREASE', 'DECREASE'):
            return cls(type='IncreaseDecrease', value=value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/NextPreviousType.java
class NextPreviousTypeModel(ItemValueBase):
    type: Literal['NextPrevious']
    value: Literal['NEXT', 'PREVIOUS']

    @override
    def get_value(self) -> Literal['NEXT', 'PREVIOUS']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('NEXT', 'PREVIOUS'):
            return cls(type='NextPrevious', value=value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/OnOffType.java
class OnOffTypeModel(ItemValueBase):
    type: Literal['OnOff']
    value: Literal['ON', 'OFF']

    @override
    def get_value(self) -> Literal['ON', 'OFF']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> Literal['ON', 'OFF']:
        return OnOffTypeModel(type='OnOff', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('ON', 'OFF'):
            return cls(type='OnOff', value=value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/OnOffType.java
class OpenClosedTypeModel(ItemValueBase):
    type: Literal['OpenClosed']
    value: Literal['OPEN', 'CLOSED']

    @override
    def get_value(self) -> Literal['OPEN', 'CLOSED']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> Literal['OPEN', 'CLOSED']:
        return OpenClosedTypeModel(type='OpenClosed', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('OPEN', 'CLOSED'):
            return cls(type='OpenClosed', value=value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PercentType.java
class PercentTypeModel(ItemValueBase):
    type: Literal['Percent']
    value: str = Field(pattern=r'^\d{1,3}(\.\d+)?$')

    @override
    def get_value(self) -> float:
        value = real(self.value)
        if 0 <= value <= 100:
            return value

        msg = f'Invalid value "{self.value!r}" for {self.__class__.__name__}'
        raise ValueError(msg)

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> float:
        return PercentTypeModel(type='Percent', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if not isinstance(value, (int, float)):
            return None

        if not 0 <= value <= 100:
            return None

        return cls(type='Percent', value=str(value))


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PlayPauseType.java
class PlayPauseTypeModel(ItemValueBase):
    type: Literal['PlayPause']
    value: Literal['PLAY', 'PAUSE']

    @override
    def get_value(self) -> Literal['PLAY', 'PAUSE']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('PLAY', 'PAUSE'):
            return cls(type='PlayPause', value=value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PointType.java
class PointTypeModel(ItemValueBase):
    type: Literal['Point']
    value: str = Field(pattern=r'^-?\d+(\.\d+)?,-?\d+(\.\d+)?(,-?\d+(\.\d+)?)?$')     # two or three entries

    @override
    def get_value(self) -> Point:
        values = self.value.split(',')
        match len(values):
            case 3:
                a, b, c = values
                return Point(real(a), real(b), real(c))
            case 2:
                a, b = values
                return Point(real(a), real(b), None)

        msg = f'Invalid value "{self.value!r}" for {self.__class__.__name__}'
        raise ValueError(msg)

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> Point:
        return PointTypeModel(type='Point', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: Point) -> Self | None:
        if isinstance(value, Point):
            a = value._latitude
            b = value._longitude
            c = value._elevation
            if c is not None:
                return cls(type='Point', value=f'{a},{b},{c}')
            return cls(type='Point', value=f'{a},{b}')

        if isinstance(value, (tuple, list)):
            if len(value) not in (2, 3) or not all(isinstance(v, (int, float)) for v in value):
                return None
            return cls(type='Point', value=','.join(str(v) for v in value))

        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/QuantityType.java
class QuantityTypeModel(ItemValueBase):
    type: Literal['Quantity']
    value: str = Field(pattern=r'^-?\d+(\.\d+)?( [^ ]+)?$')

    @override
    def get_value(self) -> QuantityInt | QuantityFloat:
        # Number:Dimensionless has no unit in the state
        if ' ' not in (value := self.value):
            unit = ''
        else:
            value, unit = value.split(' ', 1)

        # always try int
        if (nr := try_int(value, on_fail=None)) is not None:
            return QuantityInt(nr, unit)

        nr = fast_float(value)
        return QuantityFloat(nr, unit)

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> float:
        return QuantityTypeModel(type='Quantity', value=state).get_value()

    @classmethod
    def from_value(cls, value: Any) -> Self | None:
        if not isinstance(value, str):
            return None
        if (values := value.split(' ')) and len(values) != 2:
            return None
        if try_real(values[0], on_fail=None) is None:
            return None
        return cls(type='Quantity', value=value)


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/RawType.java
class RawTypeModel(ItemValueBase):
    type: Literal['Raw']
    value: str = Field(pattern=r'^data:image/[a-z_-]+;base64,[A-Za-z0-9+/]*={0,2}$')

    @override
    def get_value(self) -> RawType:
        value = self.value

        # The data is in this format
        # data:image/png;base64,iVBORw0KGgo...
        bin_type, data_str = value.split(';', 1)
        enc_str, bin_str = data_str.split(',', 1)

        if enc_str != 'base64':
            msg = f'Invalid encoding {enc_str!r} for {RawType.__name__:s}'
            raise ValueError(msg)

        return RawType.create(bin_type.removeprefix('data:'), b64decode(bin_str))

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> RawType:
        return RawTypeModel(type='Raw', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: RawType | bytes) -> Self | None:
        if isinstance(value, RawType):
            bin_type = value._type
            if not bin_type.startswith('image/'):
                bin_type = f'image/{bin_type}'
            return cls(type='Raw', value=f'data:{bin_type};base64,{b64encode(value._data).decode()}')

        if isinstance(value, bytes):
            return cls.from_value(RawType.create(None, value))

        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/RewindFastforwardType.java
class RewindFastforwardTypeModel(ItemValueBase):
    type: Literal['RewindFastforward']
    value: Literal['REWIND', 'FASTFORWARD']

    @override
    def get_value(self) -> Literal['REWIND', 'FASTFORWARD']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('REWIND', 'FASTFORWARD'):
            return cls(type='RewindFastforward', value=value)
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StopMoveType.java
class StopMoveTypeModel(ItemValueBase):
    type: Literal['StopMove']
    value: Literal['STOP', 'MOVE']

    @override
    def get_value(self) -> Literal['STOP', 'MOVE']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('STOP', 'MOVE'):
            return cls(type='StopMove', value=value)
        return None


RE_SPLIT_STRINGLIST = re.compile(r'(?<!\\),')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StringListType.java
class StringListTypeModel(ItemValueBase):
    type: Literal['StringList']
    value: str

    @override
    def get_value(self) -> tuple[str, ...]:
        if '\\' not in (value := self.value):
            return StringList(value.split(','))
        return StringList(tuple(e.replace('\\,', ',') for e in RE_SPLIT_STRINGLIST.split(value)))

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> tuple[str, ...]:
        return StringListTypeModel(type='StringList', value=state).get_value()

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: tuple[str, ...] | list[str]) -> Self | None:
        if isinstance(value, StringList):
            return cls(type='StringList', value=','.join(v.replace(',', '\\,') for v in value))

        if isinstance(value, (tuple, list)):
            values = []
            for v in value:
                if not isinstance(v, str):
                    return None
                values.append(v.replace(',', '\\,'))
            return cls(type='StringList', value=','.join(values))

        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StringType.java
class StringTypeModel(ItemValueBase):
    type: Literal['String']
    value: str

    @override
    def get_value(self) -> str:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @staticmethod
    def get_value_from_state(state: str) -> str:
        if not isinstance(state, str):
            raise TypeError()
        return state

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str | BaseModel) -> Self | None:
        if isinstance(value, str):
            return cls(type='String', value=value)
        if isinstance(value, BaseModel):
            return cls(type='String', value=value.model_dump_json(by_alias=True))
        return None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/UpDownType.java
class UpDownTypeModel(ItemValueBase):
    type: Literal['UpDown']
    value: Literal['UP', 'DOWN']

    @override
    def get_value(self) -> Literal['UP', 'DOWN']:
        return self.value

    # noinspection PyNestedDecorators
    @override
    @classmethod
    def from_value(cls, value: str) -> Self | None:
        if value in ('UP', 'DOWN'):
            return cls(type='UpDown', value=value)
        return None


OpenHabValueType = Annotated[
    RefreshTypeModel |
    UnDefTypeModel |
    DateTimeTypeModel |
    DecimalTypeModel |
    HSBTypeModel |
    IncreaseDecreaseTypeModel |
    NextPreviousTypeModel |
    OnOffTypeModel |
    OpenClosedTypeModel |
    PercentTypeModel |
    PlayPauseTypeModel |
    PointTypeModel |
    QuantityTypeModel |
    RawTypeModel |
    RewindFastforwardTypeModel |
    StopMoveTypeModel |
    StringListTypeModel |
    StringTypeModel |
    UpDownTypeModel,
    Field(discriminator='type')
]


OpenHabValueTypeAdapter = TypeAdapter[OpenHabValueType](OpenHabValueType)
