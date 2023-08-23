from __future__ import annotations

import logging
from typing import Final

from aiohttp_sse_client import client as sse_client

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.asyncio import AsyncContext
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.const.json import load_json
from HABApp.core.const.log import TOPIC_EVENTS
from HABApp.core.internals import uses_item_registry
from HABApp.core.lib import SingleTask
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.process_events import on_sse_event

Items = uses_item_registry()


class SseEventListenerPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None):
        super().__init__(name)
        self.task: Final = SingleTask(self.sse_task, name='SSE Task')

    async def on_connected(self):
        self.task.start()

    async def on_disconnected(self):
        await self.task.cancel_wait()

    async def sse_task(self):
        try:
            with AsyncContext('SSE'):
                # cache so we don't have to look up every event
                _load_json = load_json
                _see_handler = on_sse_event
                context = self.plugin_connection.context
                oh3 = context.is_oh3

                log_events = logging.getLogger(f'{TOPIC_EVENTS}.openhab')
                DEBUG = logging.DEBUG

                async with sse_client.EventSource(
                        url=f'/rest/events?topics={HABApp.CONFIG.openhab.connection.topic_filter}',
                        session=context.session, **context.session_options) as event_source:
                    async for event in event_source:

                        e_str = event.data

                        try:
                            e_json = _load_json(e_str)
                        except (ValueError, TypeError):
                            log_events.warning(f'Invalid json: {e_str}')
                            continue

                        # Alive event from openhab to detect dropped connections
                        # -> Can be ignored on the HABApp side
                        e_type = e_json.get('type')
                        if e_type == 'ALIVE':
                            continue

                        # Log raw sse event
                        if log_events.isEnabledFor(logging.DEBUG):
                            log_events._log(DEBUG, e_str, [])

                        # With OH4 we have the ItemStateUpdatedEvent, so we can ignore the ItemStateEvent
                        if not oh3 and e_type == 'ItemStateEvent':
                            continue

                        # process
                        _see_handler(e_json, oh3)
        except Exception as e:
            self.plugin_connection.process_exception(e, self.sse_task)
