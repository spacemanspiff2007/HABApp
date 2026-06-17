from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Final, Literal

from HABApp.core.asyncio import run_coro_from_thread, run_func_from_async
from HABApp.core.internals import ItemRegistryItem
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.openhab import definitions
from HABApp.openhab.definitions.helpers import OpenhabPersistenceData


if TYPE_CHECKING:
    from HABApp.openhab.connection.handler.interface_async import OpenHabAsyncInterface
    from HABApp.openhab.definitions.rest import (
        ItemChannelLinkResp,
        ItemHistoryResp,
        ItemResp,
        PersistenceServiceResp,
        RootResp,
        ThingResp,
    )
    from HABApp.openhab.definitions.rest.systeminfo import SystemInfoResp
    from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent


@HABAPP_PROVIDER.register
class OpenHabSyncInterface:
    __slots__ = ('_i',)

    def __init__(self, async_interface: OpenHabAsyncInterface) -> None:
        self._i: Final = async_interface

    def _send_websocket_event(self, event: ItemStateSendEvent | ItemCommandSendEvent) -> None:
        return run_func_from_async(self._i.send_websocket_event, event)

    def post_update(self, item: str | ItemRegistryItem, state: Any, *,
                    transport: Literal['http', 'websocket'] = 'websocket') -> None:
        """
        Post an update to the item

        :param item: item name or item
        :param state: new item state
        :param transport: transport to use. Websocket is much faster but stricter concerning which types are accepted
        """

        return run_func_from_async(self._i.post_update, item, state, transport=transport)

    def send_command(self, item: str | ItemRegistryItem, command: Any, *,
                     transport: Literal['http', 'websocket'] = 'websocket') -> None:
        """
        Send the specified command to the item

        :param item: item name or item
        :param command: command
        :param transport: transport to use. Websocket is much faster but stricter concerning which types are accepted
        """

        return run_func_from_async(self._i.send_command, item, command, transport=transport)

    # ------------------------------------------------------------------------------------------------------------------
    # Http Interface
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # root
    # ------------------------------------------------------------------------------------------------------------------
    def get_root(self) -> RootResp:
        return run_coro_from_thread(self._i.get_root(), self.get_root)

    # ------------------------------------------------------------------------------------------------------------------
    # uuid
    # ------------------------------------------------------------------------------------------------------------------
    def get_uuid(self) -> str:
        return run_coro_from_thread(self._i.get_uuid(), self.get_uuid)

    # ------------------------------------------------------------------------------------------------------------------
    # /systeminfo
    # ------------------------------------------------------------------------------------------------------------------
    def get_system_info(self) -> SystemInfoResp:
        return run_coro_from_thread(self._i.get_system_info(), self.get_system_info)

    # ------------------------------------------------------------------------------------------------------------------
    # /items
    # ------------------------------------------------------------------------------------------------------------------
    def get_item(self, item: str | ItemRegistryItem) -> ItemResp | None:
        """Return the complete openHAB item definition

        :param item: name of the item or item
        :return: openHAB item
        """
        assert isinstance(item, (str, ItemRegistryItem)), type(item)

        return run_coro_from_thread(self._i.get_item(item), self.get_item)

    def item_exists(self, item: str | ItemRegistryItem) -> bool:
        """
        Check if an item exists in the openHAB item registry

        :param item: name of the item or item
        :return: True if item was found
        """
        assert isinstance(item, (str, ItemRegistryItem)), type(item)

        return run_coro_from_thread(self._i.item_exists(item), self.item_exists)

    def remove_item(self, item: str | ItemRegistryItem) -> bool | None:
        """
        Removes an item from the openHAB item registry

        :param item: name
        :return: True if item was found and removed
        """
        assert isinstance(item, (str, ItemRegistryItem)), type(item)

        return run_coro_from_thread(self._i.remove_item(item), self.remove_item)

    def create_item(self, item_type: str, name: str,
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

        def validate(_in) -> None:
            assert isinstance(_in, str), type(_in)

        # limit values to special entries and validate parameters
        if ':' in item_type:
            __type, __unit = item_type.split(':')
            assert __unit in definitions.ITEM_DIMENSIONS, (
                f'{__unit} is not a valid openHAB unit: {", ".join(definitions.ITEM_DIMENSIONS)}'
            )
            assert __type in definitions.ITEM_TYPES, (
                f'{__type} is not a valid openHAB type: {", ".join(definitions.ITEM_TYPES)}'
            )
        else:
            assert item_type in definitions.ITEM_TYPES, (
                f'{item_type} is not an openHAB type: {", ".join(definitions.ITEM_TYPES)}'
            )
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
                assert group_function in definitions.GROUP_ITEM_FUNCTIONS, (
                    f'{item_type} is not a group function: {", ".join(definitions.GROUP_ITEM_FUNCTIONS)}'
                )

        return run_coro_from_thread(
            self._i.create_item(
                item_type, name, label=label, category=category, tags=tags, groups=groups,
                group_type=group_type, group_function=group_function, group_function_params=group_function_params
            ),
            self.create_item
        )

    def remove_metadata(self, item: str | ItemRegistryItem, namespace: str) -> bool:
        """
        Remove metadata from an item

        :param item: name of the item or item
        :param namespace: namespace
        :return: True if metadata was successfully removed
        """
        assert isinstance(item, (str, ItemRegistryItem)), type(item)
        assert isinstance(namespace, str), type(namespace)

        return run_coro_from_thread(self._i.remove_metadata(item, namespace), self.remove_metadata)

    def set_metadata(self, item: str | ItemRegistryItem, namespace: str, value: str, config: dict) -> bool:
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

        return run_coro_from_thread(self._i.set_metadata(item, namespace, value, config), self.set_metadata)

    # ------------------------------------------------------------------------------------------------------------------
    # /things
    # ------------------------------------------------------------------------------------------------------------------
    def get_thing(self, thing: str | ItemRegistryItem) -> ThingResp:
        """Return the complete openHAB thing definition

        :param thing: name of the thing or the item
        :return: openHAB thing
        """
        assert isinstance(thing, (str, ItemRegistryItem)), type(thing)

        return run_coro_from_thread(self._i.get_thing(thing), self.get_thing)

    def set_thing_cfg(self, thing: str | ItemRegistryItem, cfg: dict[str, Any]):
        return run_coro_from_thread(self._i.set_thing_cfg(thing, cfg), self.set_thing_cfg)

    def set_thing_enabled(self, thing: str | ItemRegistryItem, enabled: bool) -> int | None:  # noqa: FBT001
        """
        Enable/disable a thing

        :param thing: name of the thing or the thing object
        :param enabled: True to enable thing, False to disable thing
        """
        assert isinstance(thing, (str, ItemRegistryItem)), type(thing)

        return run_coro_from_thread(self._i.set_thing_enabled(thing, enabled), self.set_thing_enabled)

    # ------------------------------------------------------------------------------------------------------------------
    # /links
    # ------------------------------------------------------------------------------------------------------------------
    def purge_links(self) -> None:
        return run_coro_from_thread(self._i.purge_links(), self.purge_links)

    def remove_obj_links(self, name: str | ItemRegistryItem) -> bool:
        """Remove links from an item or a thing

        :param name: name of thing or item
        """
        return run_coro_from_thread(self._i.remove_obj_links(name), self.remove_obj_links)

    def get_links(self) -> tuple[ItemChannelLinkResp, ...]:
        return run_coro_from_thread(self._i.get_links(), self.get_links)

    def get_link(self, item: str | ItemRegistryItem, channel: str) -> ItemChannelLinkResp:
        """returns the link between an item and a (things) channel

        :param item: name of the item or item
        :param channel: uid of the (things) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
        """
        assert isinstance(item, (str, ItemRegistryItem)), type(item)
        assert isinstance(channel, str), type(channel)

        return run_coro_from_thread(self._i.get_link(item, channel), self.get_link)

    def create_link(self, item: str | ItemRegistryItem, channel: str,
                    configuration: dict[str, Any] | None = None) -> bool:
        """creates a link between an item and a (things) channel

        :param item: name of the item or item
        :param channel: uid of the (things) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
        :param configuration: optional configuration for the channel
        :return: True on successful creation, otherwise False
        """
        assert isinstance(item, (str, ItemRegistryItem)), type(item)
        assert isinstance(channel, str), type(channel)
        assert isinstance(configuration, dict), type(configuration)

        return run_coro_from_thread(self._i.create_link(item, channel, configuration), self.create_link)

    def remove_link(self, item: str | ItemRegistryItem, channel: str) -> None:
        """removes a link between a (things) channel and an item

        :param item: name of the item or item
        :param channel: uid of the (things) channel (usually something like AAAA:BBBBB:CCCCC:DDDD:0#SOME_NAME)
        :return: True on successful removal, otherwise False
        """
        assert isinstance(item, (str, ItemRegistryItem)), type(item)
        assert isinstance(channel, str), type(channel)

        return run_coro_from_thread(self._i.remove_link(item, channel), self.remove_link)

    # ------------------------------------------------------------------------------------------------------------------
    # /persistence
    # ------------------------------------------------------------------------------------------------------------------
    def get_persistence_services(self) -> tuple[PersistenceServiceResp, ...]:
        """Return all available persistence services"""

        return run_coro_from_thread(self._i.get_persistence_services(), self.get_persistence_services)

    def get_persistence_data(self, item: str | ItemRegistryItem, persistence: str | None,
                             start_time: datetime | None, end_time: datetime | None) -> OpenhabPersistenceData:
        """Query historical data from the openHAB persistence service

        :param item: name of the persistent item
        :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
        :param start_time: return only items which are newer than this
        :param end_time: return only items which are older than this
        :return: last stored data from persistency service
        """

        assert isinstance(item, (str, ItemRegistryItem)), type(item)
        assert isinstance(persistence, str) or persistence is None, persistence
        assert isinstance(start_time, datetime) or start_time is None, start_time
        assert isinstance(end_time, datetime) or end_time is None, end_time

        ret: Final = run_coro_from_thread(
            self._i.get_persistence_data(item, persistence, start_time, end_time),
            self.get_persistence_data
        )
        return OpenhabPersistenceData.from_resp(ret)

    def set_persistence_data(self, item: str | ItemRegistryItem, persistence: str | None,
                                   time: datetime, state: Any):
        """Set a measurement for a item in the persistence serivce

        :param item_name: name of the persistent item
        :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
        :param time: time of measurement
        :param state: state which will be set
        :return: True if data was stored in persistency service
        """
        return run_coro_from_thread(
            self._i.set_persistence_data(item, persistence, time, state), self.set_persistence_data
        )
