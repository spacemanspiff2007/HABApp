from __future__ import annotations

import datetime
from typing import Any

from HABApp.core.asyncio import run_coro_from_thread
from HABApp.core.internals import ItemRegistryItem
from .func_async import async_create_item, async_get_item, \
    async_get_thing, async_set_thing_enabled, \
    async_set_metadata, async_remove_metadata, \
    async_remove_item, async_item_exists, async_get_persistence_data, async_set_persistence_data, \
    async_get_persistence_services, async_get_link, async_create_link, async_remove_link
from HABApp.openhab import definitions
from HABApp.openhab.definitions.helpers import OpenhabPersistenceData
from HABApp.openhab.definitions.rest import ItemResp, ItemChannelLinkResp


# ----------------------------------------------------------------------------------------------------------------------
# /items
# ----------------------------------------------------------------------------------------------------------------------
# def get_items():
#     """Request all items from the openHAB Rest API. Don't use this
#     """
#     return run_coro_from_thread(async_get_items())


def get_item(item: str | ItemRegistryItem) -> ItemResp | None:
    """Return the complete openHAB item definition

    :param item: name of the item or item
    :return: openHAB item
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)

    return run_coro_from_thread(async_get_item(item), calling=get_item)


def item_exists(item: str | ItemRegistryItem):
    """
    Check if an item exists in the openHAB item registry

    :param item: name of the item or item
    :return: True if item was found
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)

    return run_coro_from_thread(async_item_exists(item), calling=item_exists)


def remove_item(item: str | ItemRegistryItem):
    """
    Removes an item from the openHAB item registry

    :param item: name
    :return: True if item was found and removed
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)

    return run_coro_from_thread(async_remove_item(item), calling=remove_item)


def create_item(item_type: str, name: str,
                label: str | None = None, category: str | None = None,
                tags: list[str] | None = None, groups: list[str] | None = None,
                group_type: str | None = None,
                group_function: str | None = None,
                group_function_params: list[str] | None = None) -> bool:
    """Creates a new item in the openHAB item registry or updates an existing one

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
            f'{__unit} is not a valid openHAB unit: {", ".join(definitions.ITEM_DIMENSIONS)}'
        assert __type in definitions.ITEM_TYPES, \
            f'{__type} is not a valid openHAB type: {", ".join(definitions.ITEM_TYPES)}'
    else:
        assert item_type in definitions.ITEM_TYPES, \
            f'{item_type} is not an openHAB type: {", ".join(definitions.ITEM_TYPES)}'
    assert isinstance(name, str), type(name)
    assert isinstance(label, str) or label is None, type(label)
    assert isinstance(category, str) or category is None, type(category)
    if tags:
        map(validate, tags)
    if groups:
        map(validate, groups)
    if group_type:
        assert isinstance(group_type, str), type(group_type)
    if group_function:
        assert isinstance(group_function, str), type(group_function)
    if group_function_params:
        map(validate, group_function_params)

    if group_type or group_function or group_function_params:
        assert item_type == 'Group', f'Item type must be "Group"! Is: {item_type}'

        if group_function:
            assert group_function in definitions.GROUP_ITEM_FUNCTIONS, \
                f'{item_type} is not a group function: {", ".join(definitions.GROUP_ITEM_FUNCTIONS)}'

    return run_coro_from_thread(
        async_create_item(
            item_type, name,
            label=label, category=category, tags=tags, groups=groups,
            group_type=group_type, group_function=group_function, group_function_params=group_function_params
        ),
        calling=create_item
    )


def set_metadata(item: str | ItemRegistryItem, namespace: str, value: str, config: dict):
    """
    Add/set metadata to an item

    :param item: name of the item or item
    :param namespace: namespace, e.g. ``stateDescription``
    :param value: value
    :param config: configuration e.g. ``{"options": "A,B,C"}``
    :return: True if metadata was successfully created/updated
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)
    assert isinstance(namespace, str), type(namespace)
    assert isinstance(value, str), type(value)
    assert isinstance(config, dict), type(config)

    return run_coro_from_thread(
        async_set_metadata(item=item, namespace=namespace, value=value, config=config), calling=set_metadata
    )


def remove_metadata(item: str | ItemRegistryItem, namespace: str):
    """
    Remove metadata from an item

    :param item: name of the item or item
    :param namespace: namespace
    :return: True if metadata was successfully removed
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)
    assert isinstance(namespace, str), type(namespace)

    return run_coro_from_thread(async_remove_metadata(item=item, namespace=namespace), calling=remove_metadata)


# ----------------------------------------------------------------------------------------------------------------------
# /things
# ----------------------------------------------------------------------------------------------------------------------
def get_thing(thing: str | ItemRegistryItem):
    """ Return the complete openHAB thing definition

    :param thing: name of the thing or the item
    :return: openHAB thing
    """
    assert isinstance(thing, (str, ItemRegistryItem)), type(thing)

    return run_coro_from_thread(async_get_thing(thing), calling=get_thing)


def set_thing_enabled(thing: str | ItemRegistryItem, enabled: bool = True):
    """
    Enable/disable a thing

    :param thing: name of the thing or the thing object
    :param enabled: True to enable thing, False to disable thing
    """
    assert isinstance(thing, (str, ItemRegistryItem)), type(thing)

    return run_coro_from_thread(async_set_thing_enabled(thing, enabled), calling=set_thing_enabled)


# ----------------------------------------------------------------------------------------------------------------------
# /persistence
# ----------------------------------------------------------------------------------------------------------------------
def get_persistence_services():
    """ Return all available persistence services
    """
    return run_coro_from_thread(async_get_persistence_services(), calling=get_persistence_services)


def get_persistence_data(item: str | ItemRegistryItem, persistence: str | None,
                         start_time: datetime.datetime | None,
                         end_time: datetime.datetime | None) -> OpenhabPersistenceData:
    """Query historical data from the openHAB persistence service

    :param item: name of the persistent item
    :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
    :param start_time: return only items which are newer than this
    :param end_time: return only items which are older than this
    :return: last stored data from persistency service
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)
    assert isinstance(persistence, str) or persistence is None, persistence
    assert isinstance(start_time, datetime.datetime) or start_time is None, start_time
    assert isinstance(end_time, datetime.datetime) or end_time is None, end_time

    ret = run_coro_from_thread(
        async_get_persistence_data(item=item, persistence=persistence, start_time=start_time, end_time=end_time),
        calling=get_persistence_data
    )
    return OpenhabPersistenceData.from_resp(ret)


def set_persistence_data(item: str | ItemRegistryItem, persistence: str | None, time: datetime.datetime, state: Any):
    """Set a measurement for a item in the persistence serivce

    :param item_name: name of the persistent item
    :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
    :param time: time of measurement
    :param state: state which will be set
    :return: True if data was stored in persistency service
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)
    assert isinstance(persistence, str) or persistence is None, persistence
    assert isinstance(time, datetime.datetime), time

    return run_coro_from_thread(
        async_set_persistence_data(item=item, persistence=persistence, time=time, state=state),
        calling=set_persistence_data
    )


# ---------------------------------------------------------------------------------------------------------------------
# Link handling is experimental
# ---------------------------------------------------------------------------------------------------------------------
def get_link(item: str | ItemRegistryItem, channel: str) -> ItemChannelLinkResp:
    """ returns the link between an item and a (things) channel

    :param item: name of the item or item
    :param channel: uid of the (things) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)
    assert isinstance(channel, str), type(channel)

    return run_coro_from_thread(async_get_link(item, channel), calling=get_link)


def create_link(
        item: str | ItemRegistryItem, channel: str, configuration: dict[str, Any] | None = None) -> bool:
    """creates a link between an item and a (things) channel

    :param item: name of the item or item
    :param channel: uid of the (things) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
    :param configuration: optional configuration for the channel
    :return: True on successful creation, otherwise False
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)
    assert isinstance(channel, str), type(channel)
    assert isinstance(configuration, dict), type(configuration)

    return run_coro_from_thread(async_create_link(item, channel, configuration), calling=create_link)


def remove_link(item: str | ItemRegistryItem, channel: str) -> bool:
    """ removes a link between a (things) channel and an item

    :param item: name of the item or item
    :param channel: uid of the (things) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
    :return: True on successful removal, otherwise False
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)
    assert isinstance(channel, str), type(channel)

    return run_coro_from_thread(async_remove_link(item, channel), calling=remove_link)
