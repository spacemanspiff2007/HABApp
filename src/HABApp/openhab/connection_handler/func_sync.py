import asyncio
import datetime
from typing import Any, Optional, List, Dict

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.const import loop
from HABApp.core.items.base_valueitem import BaseValueItem, BaseItem
from HABApp.core.wrapper import log_exception
from HABApp.openhab.definitions.rest import OpenhabItemDefinition, OpenhabThingDefinition, ItemChannelLinkDefinition
from .func_async import async_post_update, async_send_command, async_create_item, async_get_item, async_get_thing, \
    async_set_metadata, async_remove_metadata, async_get_channel_link, async_create_channel_link, \
    async_remove_channel_link, async_channel_link_exists, \
    async_remove_item, async_item_exists, async_get_persistence_data
from .. import definitions
from ..definitions.helpers import OpenhabPersistenceData


@log_exception
def post_update(item_name: str, state: Any):
    """
    Post an update to the item

    :param item_name: item name or item
    :param state: new item state
    """
    assert isinstance(item_name, (str, BaseValueItem)), type(item_name)

    if isinstance(item_name, BaseValueItem):
        item_name = item_name.name

    asyncio.run_coroutine_threadsafe(async_post_update(item_name, state), loop)


@log_exception
def send_command(item_name: str, command):
    """
    Send the specified command to the item

    :param item_name: item name or item
    :param command: command
    """
    assert isinstance(item_name, (str, HABApp.openhab.items.base_item.BaseValueItem)), type(item_name)

    if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
        item_name = item_name.name

    asyncio.run_coroutine_threadsafe(async_send_command(item_name, command), loop)


@log_exception
def create_item(item_type: str, name: str, label="", category="",
                tags: List[str] = [], groups: List[str] = [],
                group_type: str = '', group_function: str = '', group_function_params: List[str] = []):
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

    def validate(_in):
        assert isinstance(_in, str), type(_in)

    # limit values to special entries and validate parameters
    if ':' in item_type:
        __type, __unit = item_type.split(':')
        assert __unit in definitions.ITEM_DIMENSIONS, \
            f'{__unit} is not a valid Openhab unit: {", ".join(definitions.ITEM_DIMENSIONS)}'
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
        async_create_item(
            item_type, name,
            label=label, category=category, tags=tags, groups=groups,
            group_type=group_type, group_function=group_function, group_function_params=group_function_params
        ),
        loop
    )
    return fut.result()


def get_item(item_name: str, metadata: Optional[str] = None) -> OpenhabItemDefinition:
    """Return the complete OpenHAB item definition

    :param item_name: name of the item or item
    :param metadata: metadata to include (optional, comma separated or search expression)
    :return:
    """
    if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
        item_name = item_name.name
    assert isinstance(item_name, str), type(item_name)
    assert metadata is None or isinstance(metadata, str), type(metadata)

    fut = asyncio.run_coroutine_threadsafe(async_get_item(item_name, metadata=metadata), loop)
    data = fut.result()
    return OpenhabItemDefinition.parse_obj(data)


def get_thing(thing_name: str) -> OpenhabThingDefinition:
    """ Return the complete OpenHAB thing definition

    :param thing_name: name of the thing or the item
    """
    if isinstance(thing_name, BaseItem):
        thing_name = thing_name.name
    assert isinstance(thing_name, str), type(thing_name)

    fut = asyncio.run_coroutine_threadsafe(async_get_thing(thing_name), loop)
    return fut.result()


@log_exception
def remove_item(item_name: str):
    """
    Removes an item from the openHAB item registry

    :param item_name: name
    """
    fut = asyncio.run_coroutine_threadsafe(async_remove_item(item_name), loop)
    return fut.result()


def item_exists(item_name: str):
    """
    Check if an item exists in the OpenHAB item registry

    :param item_name: name
    """
    assert isinstance(item_name, str), type(item_name)
    fut = asyncio.run_coroutine_threadsafe(async_item_exists(item_name), loop)
    return fut.result()


def set_metadata(item_name: str, namespace: str, value: str, config: dict):
    """
    Add/set metadata to an item

    :param item_name: name of the item or item
    :param namespace: namespace
    :param value: value
    :param config: configuration
    :return:
    """
    if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
        item_name = item_name.name
    assert isinstance(item_name, str), type(item_name)
    assert isinstance(namespace, str), type(namespace)
    assert isinstance(value, str), type(value)
    assert isinstance(config, dict), type(config)

    fut = asyncio.run_coroutine_threadsafe(
        async_set_metadata(item=item_name, namespace=namespace, value=value, config=config), loop
    )
    return fut.result()


def remove_metadata(item_name: str, namespace: str):
    """
    Remove metadata from an item

    :param item_name: name of the item or item
    :param namespace: namespace
    :return:
    """
    if isinstance(item_name, HABApp.openhab.items.base_item.BaseValueItem):
        item_name = item_name.name
    assert isinstance(item_name, str), type(item_name)
    assert isinstance(namespace, str), type(namespace)

    fut = asyncio.run_coroutine_threadsafe(
        async_remove_metadata(item=item_name, namespace=namespace), loop
    )
    return fut.result()


def get_persistence_data(item_name: str, persistence: Optional[str],
                         start_time: Optional[datetime.datetime],
                         end_time: Optional[datetime.datetime]) -> OpenhabPersistenceData:
    """Query historical data from the OpenHAB persistence service

    :param item_name: name of the persistet item
    :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
    :param start_time: return only items which are newer than this
    :param end_time: return only items which are older than this
    """
    assert isinstance(item_name, str) and item_name, item_name
    assert isinstance(persistence, str) or persistence is None, persistence
    assert isinstance(start_time, datetime.datetime) or start_time is None, start_time
    assert isinstance(end_time, datetime.datetime) or end_time is None, end_time

    fut = asyncio.run_coroutine_threadsafe(
        async_get_persistence_data(
            item_name=item_name, persistence=persistence, start_time=start_time, end_time=end_time
        ),
        loop
    )

    ret = fut.result()
    return OpenhabPersistenceData.from_dict(ret)


# ---------------------------------------------------------------------------------------------------------------------
# Link handling is experimental
# ---------------------------------------------------------------------------------------------------------------------


def get_channel_link(channel_uid: str, item_name: str) -> ItemChannelLinkDefinition:
    """ returns the ItemChannelLinkDefinition for a link between a (things) channel and an item

    :param channel_uid: uid of the (things) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
    :param item_name: name of the item
    :return: an instance of ItemChannelLinkDefinition or None on error
    """

    assert isinstance(channel_uid, str), type(channel_uid)
    assert isinstance(item_name, str), type(item_name)

    fut = asyncio.run_coroutine_threadsafe(async_get_channel_link(channel_uid, item_name), loop)
    return fut.result()


def create_channel_link(channel_uid: str, item_name: str, configuration: Optional[Dict[str, Any]] = None) -> bool:
    """creates a link between a (things) channel and an item

    :param channel_uid: uid of the (thing) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
    :param item_name: name of the item
    :param configuration: optional configuration for the channel
    :return: true on successful creation, otherwise false
    """

    assert isinstance(channel_uid, str), type(channel_uid)
    assert isinstance(item_name, str), type(item_name)
    assert isinstance(configuration, dict), type(configuration)

    fut = asyncio.run_coroutine_threadsafe(
        async_create_channel_link(item_name=item_name, channel_uid=channel_uid, configuration=configuration),
        loop
    )
    return fut.result()


def remove_channel_link(channel_uid: str, item_name: str) -> bool:
    """ removes a link between a (things) channel and an item

    :param channel_uid: uid of the (thing) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
    :param item_name: name of the item
    :return: true on successful removal, otherwise false
    """

    fut = asyncio.run_coroutine_threadsafe(async_remove_channel_link(channel_uid, item_name), loop)
    return fut.result()


def channel_link_exists(channel_uid: str, item_name: str) -> bool:
    """ check if a things channel is linked to an item

    :param channel_uid: uid of the linked channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
    :param item_name: name of the linked item
    :return: true when the link exists, otherwise false
    """

    assert isinstance(channel_uid, str), type(channel_uid)
    assert isinstance(item_name, str), type(item_name)

    fut = asyncio.run_coroutine_threadsafe(async_channel_link_exists(channel_uid, item_name), loop)
    return fut.result()
