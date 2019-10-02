import datetime

from HABApp.core.items import Item
from . import SwitchItem, ContactItem, RollershutterItem, DimmerItem, ColorItem


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
        dt = datetime.datetime.strptime(value.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z')
        # all datetimes from openhab have a timezone set so we can't easily compare them
        # TypeError: can't compare offset-naive and offset-aware datetimes
        dt = dt.astimezone(tz=None)   # Changes datetime object so it uses system timezone
        dt = dt.replace(tzinfo=None)  # Removes timezone awareness
        return Item(name, dt)

    if openhab_type == "Color":
        if value is None:
            return ColorItem(name)
        return ColorItem(name, *(float(k) for k in value.split(',')))

    return Item(name, value)
