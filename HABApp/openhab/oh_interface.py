import asyncio
import dataclasses
import datetime
import logging
import typing

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.util import PrintException
from . import definitions
from .http_connection import HttpConnection

log = logging.getLogger('HABApp.openhab.Connection')


@dataclasses.dataclass
class OpenhabItemDefinition:
    type: str
    name: str
    state: typing.Any
    label: str = ''
    category: str = ''
    editable: bool = True
    tags: typing.List[str] = dataclasses.field(default_factory=list)
    groups: typing.List[str] = dataclasses.field(default_factory=list)
    members: 'typing.List[OpenhabItemDefinition]' = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data) -> 'OpenhabItemDefinition':
        assert isinstance(data, dict), type(dict)
        data['groups'] = data.pop('groupNames', [])

        # remove link
        data.pop('link', None)

        # map states, quick n dirty
        state = data['state']
        if state == 'NULL':
            state = None
        else:
            try:
                state = int(state)
            except ValueError:
                try:
                    state = float(state)
                except ValueError:
                    pass
        data['state'] = state

        for i, item in enumerate(data.get('members', [])):
            data['members'][i] = cls.from_dict(item)

        # Important, sometimes OpenHAB returns more than in the schema spec, so we remove those items otherwise we
        # get e.g.: TypeError: __init__() got an unexpected keyword argument 'stateDescription'
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


class OpenhabInterface:
    def __init__(self, connection):

        self.__loop = asyncio.get_event_loop()
        self.__connection: HttpConnection = connection

        # build str like this: '+1000' with the current timezone
        timezone_delta = datetime.datetime.now().astimezone().utcoffset()
        hours = int(timezone_delta.total_seconds()) // 3600
        minutes = (int(timezone_delta.total_seconds()) - hours * 3600) // 60
        self._timezone = f'{hours:+03d}{minutes:02d}'

    def __convert_to_oh_type(self, _in):
        if isinstance(_in, datetime.datetime):
            return _in.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + self._timezone
        elif isinstance(_in, HABApp.core.items.Item):
            return str(_in.value)
        elif isinstance(_in, HABApp.core.items.ColorItem):
            return f'{_in.hue:.1f},{_in.saturation:.1f},{_in.value:.1f}'
        elif isinstance(_in, (set, list, tuple, frozenset)):
            return ','.join(str(k) for k in _in)

        return str(_in)

    @PrintException
    def post_update(self, item_name: str, state):
        """
        Post an update to the item

        :param item_name: item name or item
        :param state: new item state
        """
        assert isinstance(item_name, (str, HABApp.core.items.Item)), type(item_name)

        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        if isinstance(item_name, HABApp.core.items.Item):
            item_name = item_name.name

        asyncio.run_coroutine_threadsafe(
            self.__connection.async_post_update(item_name, self.__convert_to_oh_type(state)),
            self.__loop
        )

    @PrintException
    def send_command(self, item_name: str, command):
        """
        Send the specified command to the item

        :param item_name: item name or item
        :param command: command
        """
        assert isinstance(item_name, (str, HABApp.core.items.Item)), type(item_name)

        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        if isinstance(item_name, HABApp.core.items.Item):
            item_name = item_name.name

        asyncio.run_coroutine_threadsafe(
            self.__connection.async_send_command(item_name, self.__convert_to_oh_type(command)),
            self.__loop
        )

    @PrintException
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
        :param group_function: Group state aggregation function
        :param group_function_params: params for group state aggregation
        :return: True if item was created/updated
        """
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        def validate(_in):
            assert isinstance(_in, str), type(_in)

        # limit values to special entries and validate parameters
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
                    f'{item_type} is not a group function: {", ".join(definitions.ITEM_TYPES)}'

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_create_item(
                item_type, name,
                label=label, category=category, tags=tags, groups=groups,
                group_type=group_type, group_function=group_function, group_function_params=group_function_params
            ),
            self.__loop
        )
        return fut.result()

    def get_item(self, item_name: str) -> OpenhabItemDefinition:
        """ Return the complete OpenHAB item definition

        :param item_name: name of the item or item
        """
        if isinstance(item_name, HABApp.core.items.Item):
            item_name = item_name.name
        assert isinstance(item_name, str), type(item_name)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_get_item(item_name),
            self.__loop
        )
        data = fut.result()
        return OpenhabItemDefinition.from_dict(data)

    @PrintException
    def remove_item(self, item_name: str):
        """
        Removes an item from the openHAB item registry

        :param item_name: name
        """
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_remove_item(item_name),
            self.__loop
        )
        return fut.result()

    def item_exists(self, item_name: str):
        """
        Check if an item exists in the OpenHAB item registry

        :param item_name: name
        """
        assert isinstance(item_name, str), type(item_name)
        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_item_exists(item_name),
            self.__loop
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
        if isinstance(item_name, HABApp.core.items.Item):
            item_name = item_name.name
        assert isinstance(item_name, str), type(item_name)
        assert isinstance(namespace, str), type(namespace)
        assert isinstance(value, str), type(value)
        assert isinstance(config, dict), type(config)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_set_metadata(item_name=item_name, namespace=namespace, value=value, config=config),
            self.__loop
        )
        return fut.result()

    def remove_metadata(self, item_name: str, namespace: str):
        """
        Remove metadata from an item

        :param item_name: name of the item or item
        :param namespace: namespace
        :return:
        """
        if isinstance(item_name, HABApp.core.items.Item):
            item_name = item_name.name
        assert isinstance(item_name, str), type(item_name)
        assert isinstance(namespace, str), type(namespace)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_remove_metadata(item_name=item_name, namespace=namespace),
            self.__loop
        )
        return fut.result()


OH_INTERFACE = None


def get_openhab_interface(connection=None) -> OpenhabInterface:
    global OH_INTERFACE
    if connection is None:
        return OH_INTERFACE

    OH_INTERFACE = OpenhabInterface(connection)
    return OH_INTERFACE
