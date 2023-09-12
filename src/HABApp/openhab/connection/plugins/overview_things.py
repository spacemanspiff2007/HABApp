from __future__ import annotations

import asyncio
import logging
from typing import Final

import HABApp
from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.definitions.helpers.log_table import Table

PING_CONFIG: Final = CONFIG.openhab.ping

Items = uses_item_registry()


class ThingOverviewPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None):
        super().__init__(name)

        self.do_run = True

    @HABApp.core.wrapper.log_exception
    async def on_online(self):
        if not self.do_run:
            return None

        # don't run this after the connect, let the rules load etc.
        await asyncio.sleep(90)
        self.do_run = False

        thing_data = await HABApp.openhab.interface_async.async_get_things()

        thing_table = Table('Things')
        thing_stat = thing_table.add_column('Status', align='^')
        thing_label = thing_table.add_column('Label')
        thing_location = thing_table.add_column('Location')
        thing_type = thing_table.add_column('Thing type')
        thing_uid = thing_table.add_column('Thing UID')

        zw_table = Table(heading='Z-Wave Things')
        zw_node = zw_table.add_column('Node', align='^')
        zw_stat = zw_table.add_column('Status', align='^')
        zw_label = zw_table.add_column('Label')
        zw_location = zw_table.add_column('Location')
        zw_model = zw_table.add_column('Model', align='^')
        zw_fw = zw_table.add_column('Firmware', align='^')
        zw_type = zw_table.add_column('Thing type')
        zw_uid = zw_table.add_column('Thing UID')
        # zw_l_channels = zw_table.add_column('Linked channel types')
        # zw_u_channels = zw_table.add_column('Unlinked channel types')

        for node in thing_data:
            uid = node.uid
            type_uid = node.thing_type

            is_zw = type_uid.startswith('zwave:')

            col_uid, col_stat, col_label, col_location, col_type = \
                (thing_uid, thing_stat, thing_label, thing_location, thing_type) if not is_zw else \
                (zw_uid, zw_stat, zw_label, zw_location, zw_type)

            col_uid.add(uid)
            col_type.add(type_uid)
            col_label.add(node.label)
            col_stat.add(node.status.status)
            col_location.add(node.location if node.location is not None else '')

            if not is_zw:
                continue

            # optional properties which can be set
            props = node.properties
            # channels = node.get('channels', [])

            # Node-ID, e.g. 5
            node_id = props.get('zwave_nodeid')
            zw_node.add(int(node_id) if node_id is not None else '')

            zw_model.add(props.get('modelId', ''))
            zw_fw.add(props.get('zwave_version', ''))

            # This generates very long logs and doesn't look good
            # zw_l_channels.add(
            #     tuple(map(lambda x: x.get('channelTypeUID', ''), filter(lambda x: x.get('linkedItems'), channels)))
            # )
            # zw_u_channels.add(
            #     tuple(map(lambda x: x.get('channelTypeUID', ''),
            #               filter(lambda x: not x.get('linkedItems'), channels)))
            # )

        log = logging.getLogger('HABApp.openhab.things')
        for line in thing_table.get_lines(sort_columns=[thing_uid]):
            log.info(line)

        log = logging.getLogger('HABApp.openhab.zwave')
        for line in zw_table.get_lines(sort_columns=[zw_type, 'Node']):
            log.info(line)
