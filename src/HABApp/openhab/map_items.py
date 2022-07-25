import logging
from typing import Any, Dict, FrozenSet, Optional

from immutables import Map

import HABApp
from HABApp.core.wrapper import process_exception
from HABApp.openhab.definitions.values import QuantityValue
from HABApp.openhab.items import ColorItem, ContactItem, DatetimeItem, DimmerItem, GroupItem, ImageItem, LocationItem, \
    NumberItem, PlayerItem, RollershutterItem, StringItem, SwitchItem, CallItem
from HABApp.openhab.items.base_item import HINT_TYPE_OPENHAB_ITEM
from HABApp.openhab.items.base_item import MetaData

log = logging.getLogger('HABApp.openhab')


_items: Dict[str, HINT_TYPE_OPENHAB_ITEM] = {
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


def map_item(name: str, type: str, value: Optional[str],
             label: Optional[str], tags: FrozenSet[str],
             groups: FrozenSet[str], metadata: Optional[Dict[str, Dict[str, Any]]]) -> \
        Optional['HABApp.openhab.items.OpenhabItem']:
    try:
        assert isinstance(type, str)
        assert value is None or isinstance(value, str)

        if value == 'NULL' or value == 'UNDEF':
            value = None

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

        cls = _items.get(type)
        if cls is not None:
            return cls.from_oh(name, value, label=label, tags=tags, groups=groups, metadata=meta)

        raise ValueError(f'Unknown openHAB type: {type} for {name}')

    except Exception as e:
        process_exception('map_items', e, logger=log)
        return None
