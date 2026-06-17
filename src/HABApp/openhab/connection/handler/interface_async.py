# ruff: noqa: PLR2004
from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Final, Literal
from urllib.parse import quote as quote_url

from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import ItemRegistry, ItemRegistryItem
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.openhab.definitions.helper import convert_to_oh_str
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
from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent
from HABApp.openhab.definitions.websockets.item_value_types import RawTypeModel
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


if TYPE_CHECKING:
    from datetime import datetime

    from HABApp.openhab.connection.connection import OhHttpQueue, OhWebsocketQueue
    from HABApp.openhab.connection.handler import OhClientSession
    from HABApp.openhab.definitions.rest.systeminfo import SystemInfoResp
    from HABApp.openhab.items import OpenhabItem


@HABAPP_PROVIDER.register
class OpenHabAsyncInterface:
    __slots__ = ('_client', '_get_item', '_http_queue', '_ws_queue')

    def __init__(self, websocket_queue: OhWebsocketQueue, http_queue: OhHttpQueue, client: OhClientSession,
                 ir: ItemRegistry) -> None:

        self._ws_queue: Final = websocket_queue
        self._http_queue: Final = http_queue
        self._get_item: Final = ir.get_item
        self._client: Final = client

    def _async_post_update(self, item: str | ItemRegistryItem, state: Any) -> None:
        if not isinstance(item, str):
            item = item.name
        if not isinstance(state, str):
            state = convert_to_oh_str(state)
        self._http_queue.put_nowait((item, state, False))
        return None

    def _async_send_command(self, item: str | ItemRegistryItem, state: Any) -> None:
        if not isinstance(item, str):
            item = item.name
        if not isinstance(state, str):
            state = convert_to_oh_str(state)

        self._http_queue.put_nowait((item, state, True))
        return None

    def send_websocket_event(self, event: ItemStateSendEvent | ItemCommandSendEvent) -> None:
        if not isinstance(event, (ItemStateSendEvent, ItemCommandSendEvent)):
            msg = f'Invalid event type: {type(event)}'
            raise TypeError(msg)

        # Workaround for big message sizes
        # https://github.com/openhab/openhab-core/issues/4587
        if isinstance(event.payload, RawTypeModel):
            # 'openhab/items/<NAME>/<state|command>'
            _, _, name, action = event.topic.split('/')
            self._http_queue.put_nowait((name, event.payload.value, action == 'command'))
            return None

        self._ws_queue.put_nowait(event)
        return None

    def _try_get_item(self, item: str | ItemRegistryItem) -> OpenhabItem | None:
        if isinstance(item, ItemRegistryItem):
            return item

        item_name = item.name if isinstance(item, ItemRegistryItem) else item

        if not isinstance(item_name, str):
            msg = f'Invalid item type: {type(item)}'
            raise TypeError(msg)

        try:
            item = self._get_item(item_name)
        except ItemNotFoundException:
            return None

        return item

    def post_update(self, item: str | ItemRegistryItem, state: Any, *,
                    transport: Literal['http', 'websocket'] = 'websocket') -> None:
        """
        Post an update to the item

        :param item: item name or item
        :param state: new item state
        :param transport: transport to use. Websocket is much faster but stricter concerning which types are accepted
        """

        # by default, we use the websocket connection because it's much faster
        if transport != 'websocket' or (item_obj := self._try_get_item(item)) is None:
            return self._async_post_update(item, state)

        return item_obj.oh_post_update(state)

    def send_command(self, item: str | ItemRegistryItem, command: Any, *,
                     transport: Literal['http', 'websocket'] = 'websocket') -> None:
        """
        Send the specified command to the item

        :param item: item name or item
        :param command: command
        :param transport: transport to use. Websocket is much faster but stricter concerning which types are accepted
        """

        # by default, we use the websocket connection because it's much faster
        if transport != 'websocket' or (item_obj := self._try_get_item(item)) is None:
            return self._async_send_command(item, command)

        return item_obj.oh_send_command(command)

    # ------------------------------------------------------------------------------------------------------------------
    # Http Interface
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # root
    # ------------------------------------------------------------------------------------------------------------------
    async def get_root(self) -> RootResp:
        resp: Final = await self._client.get('/rest/')
        body: Final = await resp.read()
        return RootResp.model_validate_json(body)

    async def get_root_or_none(self) -> RootResp | None:
        """Fault-tolerant so it can be used during startup"""
        resp: Final = await self._client.get('/rest/')
        if resp.status in (404, 500):
            return None

        # during startup, we sometimes get an empty response
        if not (body := await resp.read()):
            return None

        return RootResp.model_validate_json(body)

    # ------------------------------------------------------------------------------------------------------------------
    # uuid
    # ------------------------------------------------------------------------------------------------------------------
    async def get_uuid(self) -> str:
        resp: Final = await self._client.get('/rest/uuid')
        return await resp.text(encoding='utf-8')

    # ------------------------------------------------------------------------------------------------------------------
    # /systeminfo
    # ------------------------------------------------------------------------------------------------------------------
    async def get_system_info(self) -> SystemInfoResp:
        resp: Final = await self._client.get('/rest/systeminfo')

        body: Final = await resp.read()
        return SystemInfoRootResp.model_validate_json(body).system_info

    async def get_system_info_or_none(self) -> SystemInfoResp | None:
        """Fault-tolerant so it can be used during startup"""
        resp: Final = await self._client.get('/rest/systeminfo')
        if resp.status in (404, 500):
            return None

        # during startup, we sometimes get an empty response
        if not (body := await resp.read()):
            return None

        return SystemInfoRootResp.model_validate_json(body).system_info

    # ------------------------------------------------------------------------------------------------------------------
    # /items
    # ------------------------------------------------------------------------------------------------------------------
    async def get_items(self) -> tuple[ItemResp, ...]:

        resp: Final = await self._client.get('/rest/items', params={'metadata': '.+'})
        body: Final = await resp.read()

        return ItemRespList.validate_json(body)

    async def get_items_only_state(self) -> tuple[ShortItemResp, ...]:
        resp: Final = await self._client.get('/rest/items', params={'fields': 'name,state,type'})
        body: Final = await resp.read()

        return ShortItemRespList.validate_json(body)

    async def get_item(self, item: str | ItemRegistryItem) -> ItemResp | None:
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        resp: Final = await self._client.get(f'/rest/items/{item:s}', log_404=False, params={'metadata': '.+'})
        if resp.status == 404:
            return None

        body: Final = await resp.read()
        return ItemResp.model_validate_json(body)

    async def item_exists(self, item: str | ItemRegistryItem) -> bool:
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        ret: Final = await self._client.get(f'/rest/items/{item:s}', log_404=False)
        return ret.status == 200

    async def remove_item(self, item: str | ItemRegistryItem) -> bool | None:
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        if (ret := await self._client.delete(f'/rest/items/{item:s}')) is None:
            return None

        if ret.status == 404:
            raise ItemNotFoundError.from_name(item)
        if ret.status == 405:
            raise ItemNotEditableError.from_name(item)
        return ret.status < 300

    async def create_item(self, item_type: str, name: str,
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

        if (ret := await self._client.put(f'/rest/items/{name:s}', json=payload)) is None:
            return False

        if ret.status == 404:
            raise ItemNotFoundError.from_name(name)
        if ret.status == 405:
            raise ItemNotEditableError.from_name(name)
        return ret.status < 300

    async def remove_metadata(self, item: str | ItemRegistryItem, namespace: str) -> bool:
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        if (ret := await self._client.delete(f'/rest/items/{item:s}/metadata/{namespace:s}')) is None:
            return False

        if ret.status == 404:
            raise ItemNotFoundError.from_name(item)
        if ret.status == 405:
            raise MetadataNotEditableError.create_text(item, namespace)
        return ret.status < 300

    async def set_metadata(self, item: str | ItemRegistryItem, namespace: str, value: str, config: dict) -> bool:
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        payload = {
            'value': value,
            'config': config
        }
        ret = await self._client.put(f'/rest/items/{item:s}/metadata/{namespace:s}', json=payload)
        if ret is None:
            return False

        if ret.status == 404:
            raise ItemNotFoundError.from_name(item)
        if ret.status == 405:
            raise MetadataNotEditableError.create_text(item, namespace)
        return ret.status < 300

    # ------------------------------------------------------------------------------------------------------------------
    # /things
    # ------------------------------------------------------------------------------------------------------------------
    async def get_things(self) -> tuple[ThingResp, ...]:
        resp: Final = await self._client.get('/rest/things')
        body: Final = await resp.read()

        return ThingRespList.validate_json(body)

    async def get_thing(self, thing: str | ItemRegistryItem) -> ThingResp:
        # noinspection PyProtectedMember
        thing = thing if isinstance(thing, str) else thing._name

        resp: Final = await self._client.get(f'/rest/things/{thing:s}')
        if resp.status >= 300:
            raise ThingNotFoundError.from_uid(thing)

        body: Final = await resp.read()
        return ThingResp.model_validate_json(body)

    async def set_thing_cfg(self, thing: str | ItemRegistryItem, cfg: dict[str, Any]):
        # noinspection PyProtectedMember
        thing = thing if isinstance(thing, str) else thing._name

        if (ret := await self._client.put(f'/rest/things/{thing:s}/config', json=cfg)) is None:
            return None

        if ret.status == 404:
            raise ThingNotFoundError.from_uid(thing)
        if ret.status == 409:
            raise ThingNotEditableError.from_uid(thing)
        if ret.status >= 300:
            msg = 'Something went wrong'
            raise ValueError(msg)

        return ret.status

    async def set_thing_enabled(self, thing: str | ItemRegistryItem, enabled: bool) -> int | None:
        # noinspection PyProtectedMember
        thing = thing if isinstance(thing, str) else thing._name

        if (ret := await self._client.put(f'/rest/things/{thing:s}/enable', data='true' if enabled else 'false')) is None:
            return None

        if ret.status == 404:
            raise ThingNotFoundError.from_uid(thing)
        if ret.status == 409:
            raise ThingNotEditableError.from_uid(thing)
        if ret.status >= 300:
            msg = 'Something went wrong'
            raise ValueError(msg)

        return ret.status

    # ------------------------------------------------------------------------------------------------------------------
    # /links
    # ------------------------------------------------------------------------------------------------------------------
    async def purge_links(self) -> None:
        resp: Final = await self._client.post('/rest/purge')
        if resp.status != 200:
            msg = 'Unexpected error'
            raise LinkRequestError(msg)

    async def remove_obj_links(self, name: str | ItemRegistryItem) -> bool:
        """Remove links from an item or a thing

        :param name: name of thing or item
        """
        # noinspection PyProtectedMember
        name = name if isinstance(name, str) else name._name

        resp: Final = await self._client.delete(f'/rest/links/{name:s}')
        if resp.status >= 300:
            raise LinkRequestError()

        return True

    async def get_links(self) -> tuple[ItemChannelLinkResp, ...]:

        resp: Final = await self._client.get('/rest/links')
        if resp.status != 200:
            msg = 'Unexpected error'
            raise LinkRequestError(msg)

        body: Final = await resp.read()
        return ItemChannelLinkRespList.validate_json(body)

    @staticmethod
    def _get_item_link_url(item: str | ItemRegistryItem, channel: str) -> str:
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        # rest/links/ endpoint needs the channel to be url encoded
        # (AAAA:BBBB:CCCC:0#NAME -> AAAA%3ABBBB%3ACCCC%3A0%23NAME)
        # otherwise the REST-api returns HTTP-Status 500 InternalServerError
        return '/rest/links/' + quote_url(f'{item:s}/{channel:s}')

    async def get_link(self, item: str | ItemRegistryItem, channel: str) -> ItemChannelLinkResp:

        resp: Final = await self._client.get(self._get_item_link_url(item, channel), log_404=False)
        if resp.status == 200:
            body: Final = await resp.read()
            return ItemChannelLinkResp.model_validate_json(body)

        if resp.status == 404:
            raise LinkNotFoundError.from_names(item, channel)

        msg = 'Unexpected error'
        raise LinkRequestError(msg)

    async def create_link(self, item: str | ItemRegistryItem, channel: str,
                                configuration: dict[str, Any] | None = None) -> bool:

        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        # if the passed item doesn't exist OpenHAB creates a new empty item
        # this is undesired and why we raise an Exception
        if not await self.item_exists(item):
            raise ItemNotFoundError.from_name(item)

        json = {'itemName': item, 'channelUID': channel}
        if configuration is not None:
            json['configuration'] = configuration

        if (resp := await self._client.put(self._get_item_link_url(item, channel), json=json)) is None:
            return False

        if resp.status == 200:
            return True

        if resp.status == 405:
            LinkNotEditableError.from_names(item, channel)

        msg = 'Unexpected error'
        raise LinkRequestError(msg)

    async def remove_link(self, item: str | ItemRegistryItem, channel: str) -> None:

        if (resp := await self._client.delete(self._get_item_link_url(item, channel), log_404=False)) is None:
            return None
        if resp.status == 200:
            return None

        if resp.status == 404:
            raise LinkNotFoundError.from_names(item, channel)
        if resp.status == 405:
            raise LinkNotEditableError.from_names(item, channel)

        msg = 'Unexpected error'
        raise LinkRequestError(msg)

    # ------------------------------------------------------------------------------------------------------------------
    # /transformations
    # ------------------------------------------------------------------------------------------------------------------
    async def get_transformations(self) -> tuple[TransformationResp, ...]:
        resp: Final = await self._client.get('/rest/transformations')
        if resp.status >= 300:
            raise TransformationsRequestError()

        body: Final = await resp.read()
        return TransformationRespList.validate_json(body)

    # ------------------------------------------------------------------------------------------------------------------
    # /persistence
    # ------------------------------------------------------------------------------------------------------------------
    async def get_persistence_services(self) -> tuple[PersistenceServiceResp, ...]:
        resp: Final = await self._client.get('/rest/persistence')
        if resp.status >= 300:
            raise PersistenceRequestError()

        body: Final = await resp.read()
        return PersistenceServiceRespList.validate_json(body)

    async def get_persistence_data(self, item: str | ItemRegistryItem, persistence: str | None,
                                         start_time: datetime | None,
                                         end_time: datetime | None) -> ItemHistoryResp:
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        params = {}
        if persistence:
            params['serviceId'] = persistence
        if start_time is not None:
            params['starttime'] = convert_to_oh_str(start_time)
        if end_time is not None:
            params['endtime'] = convert_to_oh_str(end_time)
        if not params:
            params = None

        resp: Final = await self._client.get(f'/rest/persistence/items/{item:s}', params=params)
        if resp.status >= 300:
            raise PersistenceRequestError()

        body: Final = await resp.read()
        return ItemHistoryResp.model_validate_json(body)

    async def set_persistence_data(self, item: str | ItemRegistryItem, persistence: str | None,
                                   time: datetime, state: Any):
        # noinspection PyProtectedMember
        item = item if isinstance(item, str) else item._name

        # This does only work for some persistence services (as of OH 3.4)
        warnings.warn(f'{self.set_persistence_data.__name__} calls a part of the openHAB API which is buggy!',
                      stacklevel=2, category=ResourceWarning)

        params = {
            'time': convert_to_oh_str(time),
            'state': convert_to_oh_str(state),
        }
        if persistence is not None:
            params['serviceId'] = persistence

        ret = await self._client.put(f'/rest/persistence/items/{item:s}', params=params)
        if ret.status >= 300:
            return None
        else:
            # I would have expected the endpoint to return a valid json, but instead it returns nothing
            # return await ret.json(loads=load_json, encoding='utf-8')
            return None
