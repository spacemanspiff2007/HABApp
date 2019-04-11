import asyncio
import datetime
import logging

import HABApp
import HABApp.classes
import HABApp.core
import HABApp.openhab.events
from HABApp.config import Openhab as OpenhabConfig
from HABApp.util import PrintException
from .http_connection import HttpConnection

log = logging.getLogger('HABApp.openhab.Connection')


class OpenhabInterface:
    def __init__(self, connection, openhab_config):
        assert isinstance(openhab_config, OpenhabConfig)

        self.__config: OpenhabConfig = openhab_config
        self.__loop = asyncio.get_event_loop()
        self.__connection: HttpConnection = connection

    def __convert_to_oh_type(self, _in):
        if isinstance(_in, datetime.datetime):
            return _in.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + self.__config.general.timezone
        elif isinstance(_in, HABApp.core.Item):
            return str(_in.state)
        elif isinstance(_in, HABApp.classes.Color):
            return f'{_in.hue:.1f},{_in.saturation:.1f},{_in.value:.1f}'

        return str(_in)

    @PrintException
    def post_update(self, item_name: str, state):
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        asyncio.run_coroutine_threadsafe(
            self.__connection.async_post_update(item_name, self.__convert_to_oh_type(state)),
            self.__loop
        )

    @PrintException
    def send_command(self, item_name: str, command):
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        asyncio.run_coroutine_threadsafe(
            self.__connection.async_send_command(item_name, self.__convert_to_oh_type(command)),
            self.__loop
        )

    @PrintException
    def create_item(self, item_type: str, item_name: str, label="", category="", tags=[], groups=[]):
        if not self.__connection.is_online or self.__connection.is_read_only:
            return None

        assert isinstance(item_type, str), type(item_type)
        item_type = item_type.title()
        assert item_type in ['String', 'Number', 'Switch', 'Contact', 'Color', 'Contact'], item_type
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
