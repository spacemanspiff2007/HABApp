import datetime

from HABApp.classes import Color


def map_items(openhab_type : str, openhab_value : str):
    assert isinstance(openhab_type, str), type(openhab_type)
    assert isinstance(openhab_value, str), type(openhab_value)

    if openhab_value == 'NULL':
        return None

    if openhab_type == "Number":
        try:
            return int(openhab_value)
        except ValueError:
            return float(openhab_value)

    if openhab_type == "Decimal":
        return float(openhab_value)

    if openhab_type == "Color":
        return Color(*[float(k) for k in openhab_value.split(',')])

    if openhab_type == "DateTime":
        return datetime.datetime.strptime(openhab_value.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z')

    return openhab_value
