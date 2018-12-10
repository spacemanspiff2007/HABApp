from . import ColorItem, ContactItem, SwitchItem, DateTimeItem, StringItem


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

    return openhab_value

    if openhab_type == "String" or openhab_type == 'Location' or openhab_type == 'Player' or openhab_type == 'Group':
        _item = StringItem()
        _item.update_state(openhab_value)
        return _item

    if openhab_type == "Number":
        return int(openhab_value)

    if openhab_type == "Decimal":
        return float(openhab_value)

    if openhab_type == "Switch":
        s = SwitchItem()
        s.update_state(openhab_value)
        return s

    if openhab_type == "Contact":
        s = ContactItem()
        s.update_state(openhab_value)
        return s

    if openhab_type == "Color":
        s = ColorItem()
        s.update_state(openhab_value)
        return s

    if openhab_type == "DateTime":
        s = DateTimeItem()
        s.update_state(openhab_value)
        return s

    raise ValueError(f'Unknown Type for {openhab_type}: {openhab_value}')
