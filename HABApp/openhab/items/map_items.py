import datetime

from HABApp.classes import Color
from HABApp.core.items import Item

from . import SwitchItem, ContactItem


def map_items(name, openhab_type : str, openhab_value : str):
    assert isinstance(openhab_type, str), type(openhab_type)
    assert isinstance(openhab_value, str), type(openhab_value)

    value = openhab_value
    if openhab_value == 'NULL' or openhab_value == 'UNDEF':
        value = None

    # Specific classes
    if openhab_type == "Switch":
        return SwitchItem.from_str(name, value)
    if openhab_type == "Contact":
        return ContactItem.from_str(name, value)

    item = Item(name)
    if value is None:
        item.set_state(value)
        return item

    if openhab_type == "Number":
        try:
            value = int(openhab_value)
        except ValueError:
            value = float(openhab_value)

    elif openhab_type == "Decimal":
        value = float(openhab_value)

    elif openhab_type == "Color":
        value = Color(*[float(k) for k in openhab_value.split(',')])

    elif openhab_type == "DateTime":
        value = datetime.datetime.strptime(openhab_value.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z')

    item.set_state(value)
    return item
