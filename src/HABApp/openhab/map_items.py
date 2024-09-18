import logging
from typing import Any

from immutables import Map

from HABApp.core.wrapper import process_exception
from HABApp.openhab.definitions.values import QuantityValue
from HABApp.openhab.items import (
    CallItem,
    ColorItem,
    ContactItem,
    DatetimeItem,
    DimmerItem,
    GroupItem,
    ImageItem,
    LocationItem,
    NumberItem,
    PlayerItem,
    RollershutterItem,
    StringItem,
    SwitchItem,
)
from HABApp.openhab.items.base_item import HINT_TYPE_OPENHAB_ITEM, MetaData, OpenhabItem


log = logging.getLogger('HABApp.openhab.items')


_items: dict[str, HINT_TYPE_OPENHAB_ITEM] = {
    'String': StringItem,
    'Number': NumberItem,
    'Switch': SwitchItem,
    'Contact': ContactItem,
    'Rollershutter': RollershutterItem,
    'Dimmer': DimmerItem,
    'DateTime': DatetimeItem,
    'Color': ColorItem,
    'Image': ImageItem,
    'Group': GroupItem,
    'Player': PlayerItem,
    'Location': LocationItem,
    'Call': CallItem,
}


def map_item(name: str, type: str, value: str | None,
             label: str | None, tags: frozenset[str],
             groups: frozenset[str], metadata: dict[str, dict[str, Any]] | None) -> \
        OpenhabItem | None:
    try:
        assert isinstance(type, str)
        assert value is None or isinstance(value, str)

        # map Metadata
        if metadata is not None:
            meta = Map({k: MetaData(v['value'], Map(v.get('config', {}))) for k, v in metadata.items()})
        else:
            meta = Map()

        # Quantity types are like this: Number:Temperature and have a unit set: "12.3 °C".
        # We have to remove the dimension from the type and remove the unit from the value
        if ':' in type:
            type, dimension = type.split(':')
            # if the item is not initialized its None and has no dimension
            if value is not None:
                value, _ = QuantityValue.split_unit(value)

            # Show warning
            # https://github.com/spacemanspiff2007/HABApp/issues/383
            if 'unit' not in meta:
                log.warning(f'Item {name:s} is a UoM item but "unit" is not found in item metadata')

        cls = _items.get(type)
        if cls is not None:
            return cls.from_oh(name, value, label=label, tags=tags, groups=groups, metadata=meta)

        msg = f'Unknown openHAB type: {type} for {name}'
        raise ValueError(msg)

    except Exception as e:
        process_exception('map_items', e, logger=log)
        return None
