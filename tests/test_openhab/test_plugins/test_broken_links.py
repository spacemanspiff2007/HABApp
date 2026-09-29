from __future__ import annotations

import logging
from functools import partial
from unittest.mock import Mock

import HABApp.openhab.connection.plugins.overview_broken_links as plugin_module
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import Item
from HABApp.openhab.connection.handler import OpenHabAsyncInterface
from HABApp.openhab.definitions.rest import ItemChannelLinkResp, ThingResp
from HABApp.openhab.definitions.rest.things import ChannelResp, ThingStatusResp


async def _mock_things() -> list[ThingResp]:
    return [
        ThingResp(
            UID='thing_type:uid', thingTypeUID='thing_type',
            statusInfo=ThingStatusResp(status='ONLINE', statusDetail='NONE'),
            editable=False,
            channels=[
                ChannelResp(uid='thing_type:uid:channel1', id='channel1', channelTypeUID='channel1_type',
                            itemType='String', kind='STATE', linkedItems=[]),
                ChannelResp(uid='thing_type:uid:channel2', id='channel2', channelTypeUID='channel2_type',
                            itemType='String', kind='STATE', linkedItems=[])
            ]
        )
    ]


async def _mock_links() -> list[ItemChannelLinkResp]:
    return [
        ItemChannelLinkResp(itemName='item1', channelUID='thing_type:uid:channel1', editable=True),    # okay
        ItemChannelLinkResp(itemName='item2', channelUID='thing_type:uid:channel1', editable=True),    # item does not exist
        ItemChannelLinkResp(itemName='item1', channelUID='thing_type:uid:channel3', editable=True),    # channel does not exist
        ItemChannelLinkResp(itemName='item1', channelUID='other_thing:uid:channel1', editable=True),   # thing does not exist
    ]


async def test_link_warning(monkeypatch, ir: ItemRegistry, eb: EventBus, test_logs) -> None:
    ir.add_item(Item('item1', event_bus=Mock(EventBus)))

    mock_if = Mock(OpenHabAsyncInterface)
    mock_if.get_things = _mock_things
    mock_if.get_links = _mock_links

    p = plugin_module.BrokenLinksPlugin(item_registry=ir, interface=mock_if)
    await p.on_online()

    add = partial(test_logs.add_expected, 'HABApp.openhab.links', logging.WARNING)

    add('Item "item2" does not exist! (link between item "item2" and channel "thing_type:uid:channel1")')
    add('Channel "channel3" on thing "thing_type:uid" does not exist! '
        '(link between item "item1" and channel "thing_type:uid:channel3")')
    add('Thing "other_thing:uid" does not exist! (link between item "item1" and channel "other_thing:uid:channel1")')

    # ensure that it runs only once
    async def do_raise():
        raise ValueError()

    mock_if.get_things = do_raise
    mock_if.get_links = do_raise
    await p.on_online()
