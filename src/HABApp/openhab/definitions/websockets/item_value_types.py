import re
from datetime import datetime
from typing import Annotated, Any, Literal, override

from fastnumbers import real
from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, Field, TypeAdapter

from HABApp.core.types import HSB, Point


class BaseModel(_BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, validate_default=True, validate_assignment=True)


class ItemValueBase(BaseModel):
    def get_value(self) -> Any:
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


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/UnDefType.java
class UnDefTypeModel(ItemValueBase):
    type: Literal['UnDef']
    value: Literal['NULL', 'UNDEF']

    @override
    def get_value(self) -> None:
        return None


# ----------------------------------------------------------------------------------------------------------------------
# Library Types
# ----------------------------------------------------------------------------------------------------------------------

# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/DateTimeType.java
class DateTimeTypeModel(ItemValueBase):
    type: Literal['DateTime']
    value: datetime = Field(strict=False)

    @override
    def get_value(self) -> datetime:
        return self.value.astimezone(None).replace(tzinfo=None)


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/DecimalType.java
class DecimalTypeModel(ItemValueBase):
    type: Literal['Decimal']
    value: str

    @override
    def get_value(self) -> float:
        return real(self.value)


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/HSBType.java
class HSBTypeModel(ItemValueBase):
    type: Literal['HSB']
    value: str = Field(pattern=r'^\d+(\.\d+)?,\d+(\.\d+)?,\d+(\.\d+)?$')

    @override
    def get_value(self) -> HSB:
        h, s, b = self.value.split(',')
        return HSB(real(h), real(s), real(b))


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/IncreaseDecreaseType.java
class IncreaseDecreaseTypeModel(ItemValueBase):
    type: Literal['IncreaseDecrease']
    value: Literal['INCREASE', 'DECREASE']

    @override
    def get_value(self) -> Literal['INCREASE', 'DECREASE']:
        return self.value


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/NextPreviousType.java
class NextPreviousTypeModel(ItemValueBase):
    type: Literal['NextPrevious']
    value: Literal['NEXT', 'PREVIOUS']

    @override
    def get_value(self) -> Literal['NEXT', 'PREVIOUS']:
        return self.value


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/OnOffType.java
class OnOffTypeModel(ItemValueBase):
    type: Literal['OnOff']
    value: Literal['ON', 'OFF']

    @override
    def get_value(self) -> Literal['ON', 'OFF']:
        return self.value


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/OnOffType.java
class OpenClosedTypeModel(ItemValueBase):
    type: Literal['OpenClosed']
    value: Literal['OPEN', 'CLOSED']

    @override
    def get_value(self) -> Literal['OPEN', 'CLOSED']:
        return self.value


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


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PlayPauseType.java
class PlayPauseTypeModel(ItemValueBase):
    type: Literal['PlayPause']
    value: Literal['PLAY', 'PAUSE']

    @override
    def get_value(self) -> Literal['PLAY', 'PAUSE']:
        return self.value


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/PointType.java
class PointTypeModel(ItemValueBase):
    type: Literal['Point']
    value: str = Field(pattern=r'^\d+(\.\d+)?,\d+(\.\d+)?(,\d+(\.\d+)?)?$')     # two or three entries

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


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/QuantityType.java
class QuantityTypeModel(ItemValueBase):
    type: Literal['Quantity']
    value: str = Field(pattern=r'^\d+(\.\d+)?( [^ ]+)?$')

    @override
    def get_value(self) -> float:
        # Number:Dimensionless has no unit in the state
        if ' ' not in (value := self.value):
            return real(value)

        value, unit = value.split(' ', 1)
        return real(value)


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/RawType.java
class RawTypeModel(ItemValueBase):
    type: Literal['Raw']
    value: str = Field(pattern=r'^data:image/[a-z]+;base64,[A-Za-z0-9+/]*={0,2}$')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/RewindFastforwardType.java
class RewindFastforwardTypeModel(ItemValueBase):
    type: Literal['RewindFastforward']
    value: Literal['REWIND', 'FASTFORWARD']

    @override
    def get_value(self) -> Literal['REWIND', 'FASTFORWARD']:
        return self.value


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StopMoveType.java
class StopMoveTypeModel(ItemValueBase):
    type: Literal['StopMove']
    value: Literal['STOP', 'MOVE']

    @override
    def get_value(self) -> Literal['STOP', 'MOVE']:
        return self.value


RE_SPLIT_STRINGLIST = re.compile(r'(?<!\\),')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StringListType.java
class StringListTypeModel(ItemValueBase):
    type: Literal['StringList']
    value: str

    @override
    def get_value(self) -> tuple[str, ...]:
        if '\\' not in (value := self.value):
            return tuple(value.split(','))
        return tuple(e.replace('\\,', ',') for e in RE_SPLIT_STRINGLIST.split(value))


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/StringType.java
class StringTypeModel(ItemValueBase):
    type: Literal['String']
    value: str

    @override
    def get_value(self) -> str:
        return self.value


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/types/UpDownType.java
class UpDownTypeModel(ItemValueBase):
    type: Literal['UpDown']
    value: Literal['UP', 'DOWN']

    @override
    def get_value(self) -> Literal['UP', 'DOWN']:
        return self.value


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
