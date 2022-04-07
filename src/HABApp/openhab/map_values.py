import datetime

from HABApp.openhab.definitions import HSBValue, OnOffValue, OpenClosedValue, PercentValue, QuantityValue, RawValue, \
    UpDownValue


def map_openhab_values(openhab_type: str, openhab_value: str):
    # because we preprocess the string value can be None.
    # Either remove the preprocessing or remove this here
    if openhab_value is None:
        return None

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
        dt = datetime.datetime.strptime(openhab_value, '%Y-%m-%dT%H:%M:%S.%f%z')
        # all datetimes from openHAB have a timezone set, so we can't easily compare them
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
