from __future__ import annotations

import warnings
from datetime import datetime
from typing import Any
from urllib.parse import quote as quote_url

from HABApp.core.internals import ItemRegistryItem
from HABApp.openhab.definitions.rest import (
    ItemChannelLinkResp,
    ItemChannelLinkRespList,
    ItemHistoryResp,
    ItemResp,
    ItemRespList,
    PersistenceServiceResp,
    PersistenceServiceRespList,
    RootResp,
    ShortItemResp,
    ShortItemRespList,
    SystemInfoRootResp,
    ThingResp,
    ThingRespList,
    TransformationResp,
    TransformationRespList,
)
from HABApp.openhab.definitions.rest.habapp_data import get_api_vals, load_habapp_meta
from HABApp.openhab.errors import (
    ItemNotEditableError,
    ItemNotFoundError,
    LinkNotEditableError,
    LinkNotFoundError,
    LinkRequestError,
    MetadataNotEditableError,
    PersistenceRequestError,
    ThingNotEditableError,
    ThingNotFoundError,
    TransformationsRequestError,
)

from . import convert_to_oh_type
from .handler import delete, get, post, put


# ----------------------------------------------------------------------------------------------------------------------
# root
# ----------------------------------------------------------------------------------------------------------------------
async def async_get_root() -> RootResp | None:
    resp = await get('/rest/', log_404=False)
    if resp.status == 404 or resp.status == 500:
        return None

    # during startup, we sometimes get an empty response
    if not (b := await resp.read()):
        return None

    return RootResp.model_validate_json(b)


# ----------------------------------------------------------------------------------------------------------------------
# uuid
# ----------------------------------------------------------------------------------------------------------------------
async def async_get_uuid() -> str:
    resp = await get('/rest/uuid', log_404=False)
    return await resp.text(encoding='utf-8')


# ----------------------------------------------------------------------------------------------------------------------
# /systeminfo
# ----------------------------------------------------------------------------------------------------------------------
async def async_get_system_info():
    resp = await get('/rest/systeminfo', log_404=False)
    if resp.status == 404 or resp.status == 500:
        return None

    # during startup, we sometimes get an empty response
    if not (b := await resp.read()):
        return None

    return SystemInfoRootResp.model_validate_json(b).system_info


# ----------------------------------------------------------------------------------------------------------------------
# /items
# ----------------------------------------------------------------------------------------------------------------------
async def async_get_items() -> tuple[ItemResp, ...]:

    resp = await get('/rest/items', params={'metadata': '.+'})
    body = await resp.read()

    return ItemRespList.validate_json(body)


async def async_get_item(item: str | ItemRegistryItem) -> ItemResp | None:
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    resp = await get(f'/rest/items/{item:s}', log_404=False, params={'metadata': '.+'})
    if resp.status == 404:
        return None

    body = await resp.read()

    return ItemResp.model_validate_json(body)


async def async_get_all_items_state() -> tuple[ShortItemResp, ...]:
    resp = await get('/rest/items', params={'fields': 'name,state,type'})
    body = await resp.read()

    return ShortItemRespList.validate_json(body)


async def async_item_exists(item: str | ItemRegistryItem) -> bool:
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    ret = await get(f'/rest/items/{item:s}', log_404=False)
    return ret.status == 200


async def async_remove_item(item: str | ItemRegistryItem):
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    if (ret := await delete(f'/rest/items/{item:s}')) is None:
        return None

    if ret.status == 404:
        raise ItemNotFoundError.from_name(item)
    elif ret.status == 405:
        raise ItemNotEditableError.from_name(item)
    return ret.status < 300


async def async_create_item(item_type: str, name: str,
                            label: str | None = None, category: str | None = None,
                            tags: list[str] | None = None, groups: list[str] | None = None,
                            group_type: str | None = None,
                            group_function: str | None = None,
                            group_function_params: list[str] | None = None) -> bool:

    payload = {'type': item_type, 'name': name}
    if label:
        payload['label'] = label
    if category:
        payload['category'] = category
    if tags:
        payload['tags'] = tags
    if groups:
        payload['groupNames'] = groups  # CamelCase!

    # we create a group
    if group_type:
        payload['groupType'] = group_type   # CamelCase!
    if group_function:
        payload['function'] = {}
        payload['function']['name'] = group_function
        if group_function_params:
            payload['function']['params'] = group_function_params

    if (ret := await put(f'/rest/items/{name:s}', json=payload)) is None:
        return False

    if ret.status == 404:
        raise ItemNotFoundError.from_name(name)
    if ret.status == 405:
        raise ItemNotEditableError.from_name(name)
    return ret.status < 300


async def async_remove_metadata(item: str | ItemRegistryItem, namespace: str) -> bool:
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    if (ret := await delete(f'/rest/items/{item:s}/metadata/{namespace:s}')) is None:
        return False

    if ret.status == 404:
        raise ItemNotFoundError.from_name(item)
    elif ret.status == 405:
        raise MetadataNotEditableError.create_text(item, namespace)
    return ret.status < 300


async def async_set_metadata(item: str | ItemRegistryItem, namespace: str, value: str, config: dict) -> bool:
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    payload = {
        'value': value,
        'config': config
    }
    ret = await put(f'/rest/items/{item:s}/metadata/{namespace:s}', json=payload)
    if ret is None:
        return False

    if ret.status == 404:
        raise ItemNotFoundError.from_name(item)
    if ret.status == 405:
        raise MetadataNotEditableError.create_text(item, namespace)
    return ret.status < 300


# ----------------------------------------------------------------------------------------------------------------------
# /things
# ----------------------------------------------------------------------------------------------------------------------
async def async_get_things() -> tuple[ThingResp, ...]:
    resp = await get('/rest/things')
    body = await resp.read()

    return ThingRespList.validate_json(body)


async def async_get_thing(thing: str | ItemRegistryItem) -> ThingResp:
    # noinspection PyProtectedMember
    thing = thing if isinstance(thing, str) else thing._name

    resp = await get(f'/rest/things/{thing:s}')
    if resp.status >= 300:
        raise ThingNotFoundError.from_uid(thing)

    body = await resp.read()
    return ThingResp.model_validate_json(body)


async def async_set_thing_cfg(thing: str | ItemRegistryItem, cfg: dict[str, Any]):
    # noinspection PyProtectedMember
    thing = thing if isinstance(thing, str) else thing._name

    if (ret := await put(f'/rest/things/{thing:s}/config', json=cfg)) is None:
        return None

    if ret.status == 404:
        raise ThingNotFoundError.from_uid(thing)
    elif ret.status == 409:
        raise ThingNotEditableError.from_uid(thing)
    elif ret.status >= 300:
        raise ValueError('Something went wrong')

    return ret.status


async def async_set_thing_enabled(thing: str | ItemRegistryItem, enabled: bool):
    # noinspection PyProtectedMember
    thing = thing if isinstance(thing, str) else thing._name

    if (ret := await put(f'/rest/things/{thing:s}/enable', data='true' if enabled else 'false')) is None:
        return None

    if ret.status == 404:
        raise ThingNotFoundError.from_uid(thing)
    if ret.status == 409:
        raise ThingNotEditableError.from_uid(thing)
    if ret.status >= 300:
        msg = 'Something went wrong'
        raise ValueError(msg)

    return ret.status


# ----------------------------------------------------------------------------------------------------------------------
# /links
# ----------------------------------------------------------------------------------------------------------------------
async def async_purge_links():
    resp = await post('/rest/purge')
    if resp.status != 200:
        msg = 'Unexpected error'
        raise LinkRequestError(msg)


async def async_remove_obj_links(name: str | ItemRegistryItem) -> bool:
    """Remove links from an item or a thing

    :param name: name of thing or item
    """
    # noinspection PyProtectedMember
    name = name if isinstance(name, str) else name._name

    resp = await delete(f'/rest/links/{name:s}')
    if resp.status >= 300:
        raise LinkRequestError()

    return True


async def async_get_links() -> tuple[ItemChannelLinkResp, ...]:

    resp = await get('/rest/links')
    if resp.status != 200:
        msg = 'Unexpected error'
        raise LinkRequestError(msg)

    body = await resp.read()
    return ItemChannelLinkRespList.validate_json(body)


def __get_item_link_url(item: str | ItemRegistryItem, channel: str) -> str:
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    # rest/links/ endpoint needs the channel to be url encoded
    # (AAAA:BBBB:CCCC:0#NAME -> AAAA%3ABBBB%3ACCCC%3A0%23NAME)
    # otherwise the REST-api returns HTTP-Status 500 InternalServerError
    return '/rest/links/' + quote_url(f'{item:s}/{channel:s}')


async def async_get_link(item: str | ItemRegistryItem, channel: str) -> ItemChannelLinkResp:

    resp = await get(__get_item_link_url(item, channel), log_404=False)
    if resp.status == 200:
        body = await resp.read()
        return ItemChannelLinkResp.model_validate_json(body)

    if resp.status == 404:
        raise LinkNotFoundError.from_names(item, channel)

    msg = 'Unexpected error'
    raise LinkRequestError(msg)


async def async_create_link(
        item: str | ItemRegistryItem, channel: str, configuration: dict[str, Any] | None = None) -> bool:
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    # if the passed item doesn't exist OpenHAB creates a new empty item
    # this is undesired and why we raise an Exception
    if not await async_item_exists(item):
        raise ItemNotFoundError.from_name(item)

    json = {'itemName': item, 'channelUID': channel}
    if configuration is not None:
        json['configuration'] = configuration

    if (resp := await put(__get_item_link_url(item, channel), json=json)) is None:
        return False

    if resp.status == 200:
        return True

    if resp.status == 405:
        LinkNotEditableError.from_names(item, channel)

    msg = 'Unexpected error'
    raise LinkRequestError(msg)


async def async_remove_link(item: str | ItemRegistryItem, channel: str):

    if (resp := await delete(__get_item_link_url(item, channel), log_404=False)) is None:
        return None
    if resp.status == 200:
        return None

    if resp.status == 404:
        raise LinkNotFoundError.from_names(item, channel)
    if resp.status == 405:
        LinkNotEditableError.from_names(item, channel)

    msg = 'Unexpected error'
    raise LinkRequestError(msg)


# ----------------------------------------------------------------------------------------------------------------------
# /transformations
# ----------------------------------------------------------------------------------------------------------------------
async def async_get_transformations() -> tuple[TransformationResp, ...]:
    resp = await get('/rest/transformations')
    if resp.status >= 300:
        raise TransformationsRequestError()

    body = await resp.read()
    return TransformationRespList.validate_json(body)


# ----------------------------------------------------------------------------------------------------------------------
# /persistence
# ----------------------------------------------------------------------------------------------------------------------
async def async_get_persistence_services() -> tuple[PersistenceServiceResp, ...]:
    resp = await get('/rest/persistence')
    if resp.status >= 300:
        raise PersistenceRequestError()

    body = await resp.read()
    return PersistenceServiceRespList.validate_json(body)


async def async_get_persistence_data(item: str | ItemRegistryItem, persistence: str | None,
                                     start_time: datetime | None,
                                     end_time: datetime | None) -> ItemHistoryResp:
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    params = {}
    if persistence:
        params['serviceId'] = persistence
    if start_time is not None:
        params['starttime'] = convert_to_oh_type(start_time)
    if end_time is not None:
        params['endtime'] = convert_to_oh_type(end_time)
    if not params:
        params = None

    resp = await get(f'/rest/persistence/items/{item:s}', params=params)
    if resp.status >= 300:
        raise PersistenceRequestError()

    body = await resp.read()
    return ItemHistoryResp.model_validate_json(body)


async def async_set_persistence_data(item: str | ItemRegistryItem, persistence: str | None,
                                     time: datetime, state: Any):
    # noinspection PyProtectedMember
    item = item if isinstance(item, str) else item._name

    # This does only work for some persistence services (as of OH 3.4)
    warnings.warn(f'{async_set_persistence_data.__name__} calls a part of the openHAB API which is buggy!',
                  category=ResourceWarning)

    params = {
        'time': convert_to_oh_type(time),
        'state': convert_to_oh_type(state),
    }
    if persistence is not None:
        params['serviceId'] = persistence

    ret = await put(f'/rest/persistence/items/{item:s}', params=params)
    if ret.status >= 300:
        return None
    else:
        # I would have expected the endpoint to return a valid json, but instead it returns nothing
        # return await ret.json(loads=load_json, encoding='utf-8')
        return None


# ---------------------------------------------------------------------------------------------------------------------
# Funcs for handling HABApp Metadata
# ---------------------------------------------------------------------------------------------------------------------
async def async_remove_habapp_metadata(item: str):
    return await async_remove_metadata(item, 'HABApp')


async def async_set_habapp_metadata(item: str, obj):
    val, cfg = get_api_vals(obj)
    return await async_set_metadata(item, 'HABApp', val, cfg)


async def async_get_item_with_habapp_meta(item: str) -> ItemResp:
    if (data := await async_get_item(item)) is None:
        raise ItemNotFoundError.from_name(item)
    return load_habapp_meta(data)
