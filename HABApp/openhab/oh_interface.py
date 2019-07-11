import asyncio
import datetime
import logging

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.util import PrintException
from .http_connection import HttpConnection

log = logging.getLogger('HABApp.openhab.Connection')


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
            return str(_in.state)
        elif isinstance(_in, HABApp.core.items.ColorItem):
            return f'{_in.hue:.1f},{_in.saturation:.1f},{_in.value:.1f}'
        elif isinstance(_in, (set, list, tuple)):
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
    def create_item(self, item_type: str, item_name: str, label="", category="", tags=[], groups=[]):
        """
        Creates a new item in the openHAB item registry

        :param item_type: item type
        :param item_name: item name
        :param label: item label
        :param category: item category
        :param tags: item tags
        :param groups: in which groups is the item
        """
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        assert isinstance(item_type, str), type(item_type)
        assert item_type in ['String', 'Number', 'Switch', 'Contact', 'Dimmer', 'Rollershutter',
                             'Color', 'Contact', 'DateTime', "Location", "Player"], item_type
        assert isinstance(item_name, str), type(item_name)
        assert isinstance(label, str), type(label)
        assert isinstance(category, str), type(category)
        assert isinstance(tags, list), type(tags)
        assert isinstance(groups, list), type(groups)

        fut = asyncio.run_coroutine_threadsafe(
            self.__connection.async_create_item(item_type, item_name, label, category, tags, groups),
            self.__loop
        )
        return fut.result()

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


OH_INTERFACE = None


def get_openhab_interface(connection=None) -> OpenhabInterface:
    global OH_INTERFACE
    if connection is None:
        return OH_INTERFACE

    OH_INTERFACE = OpenhabInterface(connection)
    return OH_INTERFACE
