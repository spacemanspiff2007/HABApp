import datetime

from HABApp.core.items import Item, ColorItem
from . import SwitchItem, ContactItem, RollershutterItem, DimmerItem


def map_items(name, openhab_type : str, openhab_value : str):
    assert isinstance(openhab_type, str), type(openhab_type)
    assert isinstance(openhab_value, str), type(openhab_value)

    value = openhab_value
    if openhab_value == 'NULL' or openhab_value == 'UNDEF':
        value = None

    # Specific classes
    if openhab_type == "Switch":
        return SwitchItem(name, value)

    if openhab_type == "Contact":
        return ContactItem(name, value)

    if openhab_type == "Rollershutter":
        if value is None:
            return RollershutterItem(name, value)
        return RollershutterItem(name, float(value))

    if openhab_type == "Dimmer":
        return DimmerItem(name, value)

    if openhab_type == "Number":
        if value is None:
            return Item(name, value)

        # Number items can be int or float
        try:
            return Item(name, int(value))
        except ValueError:
            return Item(name, float(value))

    if openhab_type == "DateTime":
        if value is None:
            return Item(name, value)
        return Item(name, datetime.datetime.strptime(value.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z'))

    if openhab_type == "Color":
        if value is None:
            return ColorItem(name)
        return ColorItem(name, *(float(k) for k in value.split(',')))

    return Item(name, value)
