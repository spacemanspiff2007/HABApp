import datetime
import logging
from typing import FrozenSet, Optional

import HABApp
from HABApp.core.wrapper import process_exception
from HABApp.openhab.definitions.values import QuantityValue, RawValue
from HABApp.openhab.items import ColorItem, ContactItem, DatetimeItem, DimmerItem, GroupItem, ImageItem, LocationItem, \
    NumberItem, PlayerItem, RollershutterItem, StringItem, SwitchItem

log = logging.getLogger('HABApp.openhab')


def map_item(name: str, type: str, value: Optional[str], tags: FrozenSet[str], groups: FrozenSet[str]) -> \
        Optional['HABApp.openhab.items.OpenhabItem']:
    try:
        assert isinstance(type, str)
        assert value is None or isinstance(value, str)

        if value == 'NULL' or value == 'UNDEF':
            value = None

        # Quantity types are like this: Number:Temperature and have a unit set: "12.3 °C".
        # We have to remove the dimension from the type and remove the unit from the value
        if ':' in type:
            type, dimension = type.split(':')
            # if the item is not initialized its None and has no dimension
            if value is not None:
                value, _ = QuantityValue.split_unit(value)

        # Specific classes
        if type == "Switch":
            return SwitchItem(name, value, tags=tags, groups=groups)

        if type == "String":
            return StringItem(name, value, tags=tags, groups=groups)

        if type == "Contact":
            return ContactItem(name, value, tags=tags, groups=groups)

        if type == "Rollershutter":
            if value is None:
                return RollershutterItem(name, value, tags=tags, groups=groups)
            return RollershutterItem(name, float(value), tags=tags, groups=groups)

        if type == "Dimmer":
            if value is None:
                return DimmerItem(name, value, tags=tags, groups=groups)
            return DimmerItem(name, float(value), tags=tags, groups=groups)

        if type == "Number":
            if value is None:
                return NumberItem(name, value, tags=tags, groups=groups)

            # Number items can be int or float
            try:
                return NumberItem(name, int(value), tags=tags, groups=groups)
            except ValueError:
                return NumberItem(name, float(value), tags=tags, groups=groups)

        if type == "DateTime":
            if value is None:
                return DatetimeItem(name, value)
            # Todo: remove this once we go >= OH3.1
            # Previous OH versions used a datetime string like this:
            # 2018-11-19T09:47:38.284+0100
            # OH 3.1 uses
            # 2021-04-10T22:00:43.043996+0200
            if len(value) == 28:
                value = value.replace('+', '000+')
            dt = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
            # all datetimes from openhab have a timezone set so we can't easily compare them
            # --> TypeError: can't compare offset-naive and offset-aware datetimes
            dt = dt.astimezone(tz=None)   # Changes datetime object so it uses system timezone
            dt = dt.replace(tzinfo=None)  # Removes timezone awareness
            return DatetimeItem(name, dt, tags=tags, groups=groups)

        if type == "Color":
            if value is None:
                return ColorItem(name, tags=tags, groups=groups)
            return ColorItem(name, *(float(k) for k in value.split(',')), tags=tags, groups=groups)

        if type == "Image":
            img = ImageItem(name, tags=tags, groups=groups)
            if value is None:
                return img
            img.set_value(RawValue(value))
            return img

        if type == "Group":
            return GroupItem(name, value, tags=tags, groups=groups)

        if type == "Location":
            return LocationItem(name, value, tags=tags, groups=groups)

        if type == "Player":
            return PlayerItem(name, value, tags=tags, groups=groups)

        raise ValueError(f'Unknown Openhab type: {type} for {name}')

    except Exception as e:
        process_exception('map_items', e, logger=log)
        return None
