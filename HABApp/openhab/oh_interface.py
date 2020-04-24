import asyncio
import datetime
import logging
import typing

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.const import loop
from HABApp.core.items.base_valueitem import BaseValueItem
from HABApp.core.wrapper import log_exception
from HABApp.openhab.definitions.rest import OpenhabItemDefinition
from HABApp.openhab.definitions.rest import ItemChannelLinkDefinition
from . import definitions
from .http_connection import HttpConnection

OPTIONAL_DT = typing.Optional[datetime.datetime]

log = logging.getLogger('HABApp.openhab.Connection')



class OpenhabPersistenceData:

    def __init__(self):
        self.data: typing.Dict[float, typing.Union[int, float, str]] = {}

    @classmethod
    def from_dict(cls, data) -> 'OpenhabPersistenceData':
        c = cls()
        for entry in data['data']:
            # calc as timestamp
            time = entry['time'] / 1000
            state = entry['state']
            if '.' in state:
                try:
                    state = float(state)
                except ValueError:
                    pass
            else:
                try:
                    state = int(state)
                except ValueError:
                    pass

            c.data[time] = state
        return c

    def get_data(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None):
        if start_date is None and end_date is None:
            return self.data

        filter_start = start_date.timestamp() if start_date else None
        filter_end = end_date.timestamp() if end_date else None

        ret = {}
        for ts, val in self.data.items():
            if filter_start is not None and ts < filter_start:
                continue
            if filter_end is not None and ts > filter_end:
                continue
            ret[ts] = val
        return ret

    def min(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> typing.Optional[float]:
        return min(self.get_data(start_date, end_date).values(), default=None)

    def max(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> typing.Optional[float]:
        return max(self.get_data(start_date, end_date).values(), default=None)

    def average(self, start_date: OPTIONAL_DT = None, end_date: OPTIONAL_DT = None) -> typing.Optional[float]:
        values = list(self.get_data(start_date, end_date).values())
        ct = len(values)
        if ct == 0:
            return None
        return sum(values) / ct


class OpenhabInterface:
    def __init__(self, connection):
        self.__connection: HttpConnection = connection

    def __convert_to_oh_type(self, _in):
        if isinstance(_in, datetime.datetime):
            # Add timezone (if not yet defined) to string, then remote anything below ms.
            # 2018-11-19T09:47:38.284000+0100 -> 2018-11-19T09:47:38.284+0100
            out = _in.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            return f'{out[:-8]}{out[-5:]}'
        elif isinstance(_in, HABApp.openhab.items.ColorItem):
            return f'{_in.hue:.1f},{_in.saturation:.1f},{_in.value:.1f}'
        elif isinstance(_in, BaseValueItem):
            return str(_in.value)
        elif isinstance(_in, (set, list, tuple, frozenset)):
            return ','.join(str(k) for k in _in)
        elif _in is None:
            return 'NULL'

        return str(_in)

    @log_exception
    def post_update(self, item_name: str, state):
        """
        Post an update to the item

        :param item_name: item name or item
        :param state: new item state
        """
        assert isinstance(item_name, (str, HABApp.openhab.items.base_item.BaseValueItem)), type(item_name)

        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
            item_name = item_name.name

        asyncio.run_coroutine_threadsafe(
            self.__connection.async_post_update(item_name, self.__convert_to_oh_type(state)),
            loop
        )

    @log_exception
    def send_command(self, item_name: str, command):
        """
        Send the specified command to the item

        :param item_name: item name or item
        :param command: command
        """
        assert isinstance(item_name, (str, HABApp.openhab.items.base_item.BaseValueItem)), type(item_name)

        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
            item_name = item_name.name

        asyncio.run_coroutine_threadsafe(
            self.__connection.async_send_command(item_name, self.__convert_to_oh_type(command)),
            loop
        )

    @log_exception
    def create_item(self, item_type: str, name: str, label="", category="",
                    tags: typing.List[str] = [], groups: typing.List[str] = [],
                    group_type: str = '', group_function: str = '', group_function_params: typing.List[str] = []):
        """Creates a new item in the OpenHAB item registry or updates an existing one

        :param item_type: item type
        :param name: item name
        :param label: item label
        :param category: item category
        :param tags: item tags
        :param groups: in which groups is the item
        :param group_type: what kind of group is it
        :param group_function: group state aggregation function
        :param group_function_params: params for group state aggregation
        :return: True if item was created/updated
        """
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        def validate(_in):
            assert isinstance(_in, str), type(_in)

        # limit values to special entries and validate parameters
        if ':' in item_type:
            __type, __unit = item_type.split(':')
            assert __unit in definitions.ITEM_DIMENSION, \
                f'{__unit} is not a valid Openhab unit: {", ".join(definitions.ITEM_DIMENSION)}'
            assert __type in definitions.ITEM_TYPES, \
                f'{__type} is not a valid OpenHAB type: {", ".join(definitions.ITEM_TYPES)}'
        else:
            assert item_type in definitions.ITEM_TYPES, \
                f'{item_type} is not an OpenHAB type: {", ".join(definitions.ITEM_TYPES)}'
        assert isinstance(name, str), type(name)
        assert isinstance(label, str), type(label)
        assert isinstance(category, str), type(category)
        map(validate, tags)
        map(validate, groups)
        assert isinstance(group_type, str), type(group_type)
        assert isinstance(group_function, str), type(group_function)
        map(validate, group_function_params)

        if group_type or group_function or group_function_params:
            assert item_type == 'Group', f'Item type must be "Group"! Is: {item_type}'

            if group_function:
                assert group_function in definitions.GROUP_FUNCTIONS, \
                    f'{item_type} is not a group function: {", ".join(definitions.GROUP_FUNCTIONS)}'

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_create_item(
                item_type, name,
                label=label, category=category, tags=tags, groups=groups,
                group_type=group_type, group_function=group_function, group_function_params=group_function_params
            ),
            loop
        )
        return fut.result()

    def get_item(self, item_name: str) -> OpenhabItemDefinition:
        """ Return the complete OpenHAB item definition

        :param item_name: name of the item or item
        """
        if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
            item_name = item_name.name
        assert isinstance(item_name, str), type(item_name)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_get_item(item_name),
            loop
        )
        data = fut.result()
        return OpenhabItemDefinition.parse_obj(data)

    def thing_get_link(self, channel_uid: str, item_name: str) -> ItemChannelLinkDefinition:
        """ returns the ItemChannelLinkDefinition for a link between a things channel and an item

        :param channel_uid: uid of the channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
        :param item_name: name of the item
        """

        assert isinstance(channel_uid, str), type(channel_uid)
        assert isinstance(item_name, str), type(item_name)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_thing_get_link(channel_uid, item_name),
            loop
        )
        return fut.result()

    def thing_add_link(self, link_def: ItemChannelLinkDefinition) -> bool:
        """ adds a link between a things channel and an item

        :param link_def: an instance of ItemChannelLinkDefinition with at least channel_uid and item_name set
        """

        assert isinstance(link_def, ItemChannelLinkDefinition), type(link_def)
        assert isinstance(link_def.item_name, str), type(link_def.item_name)
        assert isinstance(link_def.channel_uid, str), type(link_def.channel_uid)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_thing_add_link(link_def),
            loop
        )
        return fut.result()

    def thing_remove_link(self, channel_uid: str, item_name: str) -> bool:
        """ removes a link between a things channel and an item

        :param channel_uid: uid of the channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
        :param item_name: name of the item
        """

        link = ItemChannelLinkDefinition(itemName=item_name, channelUID=channel_uid)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_thing_remove_link(link),
            loop
        )
        return fut.result()

    def thing_link_exists(self, channel_uid: str, item_name: str) -> bool:
        """ check if a things channel is linked to an item

        :param channel_uid: uid of the linked channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
        :param item_name: name of the linked item
        """

        assert isinstance(channel_uid, str), type(channel_uid)
        assert isinstance(item_name, str), type(item_name)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_thing_link_exists(channel_uid, item_name),
            loop
        )
        return fut.result()

    @log_exception
    def remove_item(self, item_name: str):
        """
        Removes an item from the openHAB item registry

        :param item_name: name
        """
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_remove_item(item_name),
            loop
        )
        return fut.result()

    def item_exists(self, item_name: str):
        """
        Check if an item exists in the OpenHAB item registry

        :param item_name: name
        """
        if not self.__connection.is_online:
            return None

        assert isinstance(item_name, str), type(item_name)
        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_item_exists(item_name),
            loop
        )
        return fut.result()

    def set_metadata(self, item_name: str, namespace: str, value: str, config: dict):
        """
        Add/set metadata to an item

        :param item_name: name of the item or item
        :param namespace: namespace
        :param value: value
        :param config: configuration
        :return:
        """
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
            item_name = item_name.name
        assert isinstance(item_name, str), type(item_name)
        assert isinstance(namespace, str), type(namespace)
        assert isinstance(value, str), type(value)
        assert isinstance(config, dict), type(config)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_set_metadata(item_name=item_name, namespace=namespace, value=value, config=config),
            loop
        )
        return fut.result()

    def remove_metadata(self, item_name: str, namespace: str):
        """
        Remove metadata from an item

        :param item_name: name of the item or item
        :param namespace: namespace
        :return:
        """
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
            item_name = item_name.name
        assert isinstance(item_name, str), type(item_name)
        assert isinstance(namespace, str), type(namespace)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_remove_metadata(item_name=item_name, namespace=namespace),
            loop
        )
        return fut.result()

    def get_persistence_data(self,
                             item_name: str, persistence: typing.Optional[str],
                             start_time: typing.Optional[datetime.datetime],
                             end_time: typing.Optional[datetime.datetime]) -> OpenhabPersistenceData:
        """Query historical data from the OpenHAB persistence service

        :param item_name: name of the persistet item
        :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
        :param start_time: return only items which are newer than this
        :param end_time: return only items which are older than this
        """
        if not self.__connection.is_online:
            return None

        assert isinstance(item_name, str) and item_name, item_name
        assert isinstance(persistence, str) or persistence is None, persistence
        assert isinstance(start_time, datetime.datetime) or start_time is None, start_time
        assert isinstance(end_time, datetime.datetime) or end_time is None, end_time

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.get_persistence_data(
                item_name=item_name, persistence=persistence, start_time=start_time, end_time=end_time
            ),
            loop
        )

        ret = fut.result()
        return OpenhabPersistenceData.from_dict(ret)


OH_INTERFACE = None


def get_openhab_interface(connection=None) -> OpenhabInterface:
    global OH_INTERFACE
    if connection is None:
        return OH_INTERFACE

    OH_INTERFACE = OpenhabInterface(connection)
    return OH_INTERFACE
