import pytest

from HABApp.openhab.definitions import ITEM_DIMENSION
from HABApp.openhab.definitions import PercentValue, UpDownValue, OnOffValue, HSBValue, QuantityValue, OpenClosedValue


@pytest.mark.parametrize(
    "cls,values", [
        (UpDownValue, (UpDownValue.DOWN, UpDownValue.UP)),
        (OnOffValue, (OnOffValue.ON, OnOffValue.OFF)),
        (OpenClosedValue, (OpenClosedValue.OPEN, OpenClosedValue.CLOSED)),
    ]
)
def test_val_same_type(cls, values):
    for val in values:
        assert cls(val).value == val


@pytest.mark.parametrize(
    "cls,values", [
        (PercentValue, (('0', 0.0), ('5', 5.0), ('55.5', 55.5), ('100.0', 100), )),
        (HSBValue, (
            ('0,0,0', (0, 0, 0)), ('5,0,0', (5, 0, 0)),
            ('100.0,0,360', (100, 0, 360)), ('0,100.0,180', (0, 100, 180))
        )),
    ]
)
def test_val_convert(cls, values):
    for val in values:
        assert cls(val[0]).value == val[1]


def test_quantity_value():
    unit_of_dimension = {
        'Length': 'm', 'Temperature': '°C', 'Pressure': 'hPa', 'Speed': 'km/h', 'Intensity': 'W/m²', 'Angle': '°'
    }

    for dimension in ITEM_DIMENSION:
        for val in (-103.3, -3, 0, 0.33535, 5, 55.5, 105.5):
            unit = unit_of_dimension[dimension]
            v = QuantityValue(f'{val} {unit}')
            assert v.value == val
            assert v.unit == unit
