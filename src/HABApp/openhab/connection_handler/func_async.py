import datetime
import traceback
import typing
from typing import Any, Optional, Dict, List
from urllib.parse import quote as quote_url

from HABApp.core.const.json import load_json
from HABApp.core.items import BaseValueItem
from HABApp.openhab.exceptions import OpenhabDisconnectedError, OpenhabNotReadyYet, ThingNotEditableError, \
    ThingNotFoundError, ItemNotEditableError, ItemNotFoundError, MetadataNotEditableError
from HABApp.openhab.definitions.rest import ItemChannelLinkDefinition, LinkNotFoundError, OpenhabThingDefinition
from HABApp.openhab.definitions.rest.habapp_data import get_api_vals, load_habapp_meta
from .http_connection import delete, get, post, put, log, async_get_root, async_get_uuid


if typing.TYPE_CHECKING:
    async_get_root = async_get_root
    async_get_uuid = async_get_uuid


def convert_to_oh_type(_in: Any) -> str:
    if isinstance(_in, datetime.datetime):
        # Add timezone (if not yet defined) to string, then remote anything below ms.
        # 2018-11-19T09:47:38.284000+0100 -> 2018-11-19T09:47:38.284+0100
        out = _in.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        return f'{out[:-8]}{out[-5:]}'
    elif isinstance(_in, BaseValueItem):
        return str(_in.value)
    elif isinstance(_in, (set, list, tuple, frozenset)):
        return ','.join(str(k) for k in _in)
    elif _in is None:
        return 'NULL'

    return str(_in)


async def async_post_update(item, state: Any):
    if not isinstance(state, str):
        state = convert_to_oh_type(state)
    await put(f'items/{item:s}/state', data=state)


async def async_send_command(item, state: Any):
    if not isinstance(state, str):
        state = convert_to_oh_type(state)
    await post(f'items/{item:s}', data=state)


async def async_item_exists(item) -> bool:
    ret = await get(f'items/{item:s}', log_404=False)
    return ret.status == 200


async def async_get_items(include_habapp_meta=False) -> Optional[List[Dict[str, Any]]]:
    params = None
    if include_habapp_meta:
        params = {'metadata': 'HABApp'}

    try:
        resp = await get('items', params=params)
        return load_json(await resp.text(encoding='utf-8'))
    except Exception as e:
        # sometimes uuid already works but items not - so we ignore these errors here, too
        if not isinstance(e, (OpenhabDisconnectedError, OpenhabNotReadyYet)):
            for line in traceback.format_exc().splitlines():
                log.error(line)
        return None


async def async_get_item(item: str, metadata: Optional[str] = None) -> dict:
    params = None if metadata is None else {'metadata': metadata}
    ret = await get(f'items/{item:s}', params=params, log_404=False)
    if ret.status == 404:
        raise ItemNotFoundError.from_name(item)
    if ret.status >= 300:
        return {}
    else:
        data = await ret.json(encoding='utf-8')
        try:
            data['groups'] = data.pop('groupNames')
        except KeyError:
            pass
        return data


async def async_get_things() -> Optional[List[Dict[str, Any]]]:

    try:
        resp = await get('things')
        return load_json(await resp.text(encoding='utf-8'))
    except Exception as e:
        # sometimes uuid and items already works but things not - so we ignore these errors here, too
        if not isinstance(e, (OpenhabDisconnectedError, OpenhabNotReadyYet)):
            for line in traceback.format_exc().splitlines():
                log.error(line)
        return None


async def async_get_thing(uid: str) -> OpenhabThingDefinition:
    ret = await get(f'things/{uid:s}')
    if ret.status >= 300:
        raise ThingNotFoundError.from_uid(uid)

    return OpenhabThingDefinition.parse_obj(await ret.json(encoding='utf-8'))


async def async_get_persistence_data(item_name: str, persistence: typing.Optional[str],
                                     start_time: typing.Optional[datetime.datetime],
                                     end_time: typing.Optional[datetime.datetime]) -> dict:

    params = {}
    if persistence:
        params['serviceId'] = persistence
    if start_time is not None:
        params['starttime'] = start_time.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    if end_time is not None:
        params['endtime'] = end_time.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    if not params:
        params = None

    ret = await get(f'persistence/items/{item_name:s}', params=params)
    if ret.status >= 300:
        return {}
    else:
        return await ret.json(encoding='utf-8')


async def async_create_item(item_type, name, label="", category="", tags=[], groups=[],
                            group_type=None, group_function=None, group_function_params=[]) -> bool:

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

    ret = await put(f'items/{name:s}', json=payload)
    if ret is None:
        return False

    if ret.status == 404:
        raise ItemNotFoundError.from_name(name)
    elif ret.status == 405:
        raise ItemNotEditableError.from_name(name)
    return ret.status < 300


async def async_remove_item(item):
    await delete(f'items/{item:s}')


async def async_remove_metadata(item: str, namespace: str):
    ret = await delete(f'items/{item:s}/metadata/{namespace:s}')
    if ret is None:
        return False

    if ret.status == 404:
        raise ItemNotFoundError.from_name(item)
    elif ret.status == 405:
        raise MetadataNotEditableError.create_text(item, namespace)
    return ret.status < 300


async def async_set_metadata(item: str, namespace: str, value: str, config: dict):
    payload = {
        'value': value,
        'config': config
    }
    ret = await put(f'items/{item:s}/metadata/{namespace:s}', json=payload)
    if ret is None:
        return False

    if ret.status == 404:
        raise ItemNotFoundError.from_name(item)
    elif ret.status == 405:
        raise MetadataNotEditableError.create_text(item, namespace)
    return ret.status < 300


async def async_set_thing_cfg(uid: str, cfg: typing.Dict[str, typing.Any]):
    ret = await put(f'things/{uid:s}/config', json=cfg)
    if ret is None:
        return None

    if ret.status == 404:
        raise ThingNotFoundError.from_uid(uid)
    elif ret.status == 409:
        raise ThingNotEditableError.from_uid(uid)
    elif ret.status >= 300:
        raise ValueError('Something went wrong')

    return ret.status


# ---------------------------------------------------------------------------------------------------------------------
# Link handling is experimental
# ---------------------------------------------------------------------------------------------------------------------

def __get_link_url(channel_uid: str, item_name: str) -> str:
    # rest/links/ endpoint needs the channel to be url encoded
    # (AAAA:BBBB:CCCC:0#NAME -> AAAA%3ABBBB%3ACCCC%3A0%23NAME)
    # otherwise the REST-api returns HTTP-Status 500 InternalServerError
    return 'links/' + quote_url(f"{item_name}/{channel_uid}")


async def async_remove_channel_link(channel_uid: str, item_name: str) -> bool:
    ret = await delete(__get_link_url(channel_uid, item_name))
    if ret is None:
        return False
    return ret.status == 200


async def async_get_channel_links() -> List[Dict[str, str]]:
    ret = await get('links')
    if ret.status >= 300:
        return None
    else:
        return await ret.json(encoding='utf-8')


async def async_get_channel_link_mode_auto() -> bool:
    ret = await get('links/auto')
    if ret.status >= 300:
        return False
    else:
        return await ret.json(encoding='utf-8')


async def async_get_channel_link(channel_uid: str, item_name: str) -> ItemChannelLinkDefinition:
    ret = await get(__get_link_url(channel_uid, item_name), log_404=False)
    if ret.status == 404:
        raise LinkNotFoundError(f'Link {item_name} -> {channel_uid} not found!')
    if ret.status >= 300:
        return None
    else:
        return ItemChannelLinkDefinition(**await ret.json(encoding='utf-8'))


async def async_channel_link_exists(channel_uid: str, item_name: str) -> bool:
    ret = await get(__get_link_url(channel_uid, item_name), log_404=False)
    return ret.status == 200


async def async_create_channel_link(
        channel_uid: str, item_name: str, configuration: Optional[Dict[str, Any]] = None) -> bool:

    # if the passed item doesn't exist OpenHAB creates a new empty item item
    # this is undesired and why we raise an Exception
    if not await async_item_exists(item_name):
        raise ItemNotFoundError.from_name(item_name)

    ret = await put(
        __get_link_url(channel_uid, item_name),
        json={'configuration': configuration} if configuration is not None else {}
    )
    if ret is None:
        return False
    return ret.status == 200


# ---------------------------------------------------------------------------------------------------------------------
# Funcs for handling HABApp Metadata
# ---------------------------------------------------------------------------------------------------------------------
async def async_remove_habapp_metadata(item: str):
    return await async_remove_metadata(item, 'HABApp')


async def async_set_habapp_metadata(item: str, obj):
    val, cfg = get_api_vals(obj)
    return await async_set_metadata(item, 'HABApp', val, cfg)


async def async_get_item_with_habapp_meta(item: str) -> dict:
    data = await async_get_item(item, metadata='HABApp')
    return load_habapp_meta(data)
