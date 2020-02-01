import datetime

from HABApp.openhab.definitions import HSBValue, OnOffValue, OpenClosedValue, PercentValue, QuantityValue, RawValue, \
    UpDownValue


def map_openhab_values(openhab_type: str, openhab_value: str):
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
        dt = datetime.datetime.strptime(openhab_value.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z')
        # all datetimes from openhab have a timezone set so we can't easily compare them
        # --> TypeError: can't compare offset-naive and offset-aware datetimes
        dt = dt.astimezone(tz=None)   # Changes datetime object so it uses system timezone
        dt = dt.replace(tzinfo=None)  # Removes timezone awareness
        return dt

    if openhab_type == "HSB":
        return HSBValue(openhab_value)

    if openhab_type == 'OnOff':
        return OnOffValue(openhab_value)

    if openhab_type == 'OpenClosed':
        return OpenClosedValue(openhab_value)

    if openhab_type == 'UpDown':
        return UpDownValue(openhab_value)

    if openhab_type == 'Percent':
        return PercentValue(openhab_value)

    if openhab_type == 'Quantity':
        return QuantityValue(openhab_value)

    if openhab_type == 'Raw':
        return RawValue(openhab_value)

    return openhab_value
