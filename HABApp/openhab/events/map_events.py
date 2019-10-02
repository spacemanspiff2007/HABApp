import datetime

from ..definitions import PercentValue, UpDownValue, OnOffValue, HSBValue


def map_event_types(openhab_type: str, openhab_value: str):
    assert isinstance(openhab_type, str), type(openhab_type)
    assert isinstance(openhab_value, str), type(openhab_value)

    if openhab_type == 'UnDef' or openhab_value == 'NULL':
        return None

    if openhab_type == "Number":
        return int(openhab_value)

    if openhab_type == "Decimal":
        try:
            return int(openhab_value)
        except ValueError:
            return float(openhab_value)

    if openhab_type == "DateTime":
        # 2018-11-19T09:47:38.284+0100
        return datetime.datetime.strptime(openhab_value.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z')

    if openhab_type == "HSB":
        return HSBValue(openhab_value)

    if openhab_type == 'OnOff':
        return OnOffValue(openhab_value)

    if openhab_type == 'UpDown':
        return UpDownValue(openhab_value)

    if openhab_type == 'Percent':
        return PercentValue(openhab_value)

    return openhab_value
