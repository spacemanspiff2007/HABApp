import datetime
import logging
import typing

from HABApp.core.items.base_item import BaseItem
from HABApp.core.wrapper import process_exception
from HABApp.openhab.definitions.values import QuantityValue, RawValue
from HABApp.openhab.items import ColorItem, ContactItem, DatetimeItem, DimmerItem, GroupItem, ImageItem, LocationItem, \
    NumberItem, PlayerItem, RollershutterItem, StringItem, SwitchItem

log = logging.getLogger('HABApp.openhab')


def map_item(name, openhab_type: str, openhab_value: str) -> typing.Optional[BaseItem]:
    try:
        assert isinstance(openhab_type, str), type(openhab_type)
        assert isinstance(openhab_value, str), type(openhab_value)

        value: typing.Optional[str] = openhab_value
        if openhab_value == 'NULL' or openhab_value == 'UNDEF':
            value = None

        # Quantity types are like this: Number:Temperature and have a unit set: "12.3 °C".
        # We have to remove the dimension from the type and remove the unit from the value
        if ':' in openhab_type:
            openhab_type, dimension = openhab_type.split(':')
            # if the item is not initialized its None and has no dimension
            if value is not None:
                value, _ = QuantityValue.split_unit(value)

        # Specific classes
        if openhab_type == "Switch":
            return SwitchItem(name, value)

        if openhab_type == "String":
            return StringItem(name, value)

        if openhab_type == "Contact":
            return ContactItem(name, value)

        if openhab_type == "Rollershutter":
            if value is None:
                return RollershutterItem(name, value)
            return RollershutterItem(name, float(value))

        if openhab_type == "Dimmer":
            if value is None:
                return DimmerItem(name, value)
            return DimmerItem(name, float(value))

        if openhab_type == "Number":
            if value is None:
                return NumberItem(name, value)

            # Number items can be int or float
            try:
                return NumberItem(name, int(value))
            except ValueError:
                return NumberItem(name, float(value))

        if openhab_type == "DateTime":
            if value is None:
                return DatetimeItem(name, value)
            dt = datetime.datetime.strptime(value.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z')
            # all datetimes from openhab have a timezone set so we can't easily compare them
            # --> TypeError: can't compare offset-naive and offset-aware datetimes
            dt = dt.astimezone(tz=None)   # Changes datetime object so it uses system timezone
            dt = dt.replace(tzinfo=None)  # Removes timezone awareness
            return DatetimeItem(name, dt)

        if openhab_type == "Color":
            if value is None:
                return ColorItem(name)
            return ColorItem(name, *(float(k) for k in value.split(',')))

        if openhab_type == "Image":
            img = ImageItem(name)
            if value is None:
                return img
            img.set_value(RawValue(value))
            return img

        if openhab_type == "Group":
            return GroupItem(name, value)

        if openhab_type == "Location":
            return LocationItem(name, value)

        if openhab_type == "Player":
            return PlayerItem(name, value)

        raise ValueError(f'Unknown Openhab type: {openhab_type} for {name}')

    except Exception as e:
        process_exception('map_items', e, logger=log)
        return None
