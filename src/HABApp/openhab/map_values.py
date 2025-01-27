from typing import Final

from HABApp.openhab.definitions.oh_types import ALL_TYPES, DecimalType, OpenHABDataType, UnDefType
from HABApp.openhab.definitions.values import ALL_VALUES, ComplexOhValue


_values: Final[dict[str, type[ComplexOhValue] | type[OpenHABDataType]]] = {}


def _fill_values() -> None:
    def _assign(classes: tuple[type[ComplexOhValue] | type[OpenHABDataType], ...], suffix: str) -> None:
        for cls in classes:
            name = cls.__name__
            assert name.endswith(suffix)  # noqa: S101
            name = name.removesuffix(suffix)
            _values[name] = cls

    _assign(ALL_TYPES, 'Type')
    _assign(ALL_VALUES, 'Value')

    # Somehow also we have number values
    _values['Number'] = DecimalType


_fill_values()
del _fill_values

NONE_VALUES: Final = (UnDefType.NULL, UnDefType.UNDEF)

def map_openhab_values(openhab_type: str, openhab_value: str):
    if openhab_value in NONE_VALUES:
        return None

    if (cls := _values.get(openhab_type)) is None:
        msg = f'Unknown type {openhab_type}'
        raise ValueError(msg)

    return cls.from_oh_str(openhab_value)
