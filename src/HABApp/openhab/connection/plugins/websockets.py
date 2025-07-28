from __future__ import annotations

import logging
from asyncio import Queue, sleep
from base64 import b64encode
from typing import Final

from aiohttp import BasicAuth, ClientError, ClientWebSocketResponse, WSMsgType
from pydantic import ValidationError

import HABApp
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.const.const import PYTHON_311
from HABApp.core.const.log import TOPIC_EVENTS
from HABApp.core.internals import uses_item_registry
from HABApp.core.lib import SingleTask
from HABApp.core.logger import HABAppError, HABAppWarning
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.definitions.helpers import get_discriminator_values_from_union
from HABApp.openhab.definitions.websockets import (
    OPENHAB_EVENT_TYPE_ADAPTER,
    OpenHabEventType,
    WebsocketHeartbeatEvent,
    WebsocketSendTypeFilter,
    WebsocketTopicEnum,
)
from HABApp.openhab.definitions.websockets.base import BaseOutEvent
from HABApp.openhab.process_events import on_openhab_event


if PYTHON_311:
    from asyncio import TaskGroup
else:
    from taskgroup import TaskGroup


class WebSocketClosedError(ClientError):
    pass


Items = uses_item_registry()


class WebsocketPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.task: Final = SingleTask(self.websockets_task, name='WebsocketsEventsTask')

        self._websocket: ClientWebSocketResponse | None = None
        self.queue: Queue[BaseOutEvent] | None = None

        self._sent_events: Final[dict[str, BaseOutEvent]] = {}

    async def on_connected(self, context: OpenhabContext) -> None:
        self.queue: Queue[BaseOutEvent] = context.out_queue
        self.task.start()

    async def on_disconnected(self) -> None:
        await self.task.cancel_wait()
        self._sent_events.clear()

    @staticmethod
    def _build_token(auth: BasicAuth) -> str:
        login = auth.login
        password = auth.password

        # we use token as auth
        for v in (login, password):
            if v.startswith('oh.'):
                return v

        # basic auth
        return b64encode(f'{login}:{password}'.encode()).decode()

    async def _websocket_sender(self, ws: ClientWebSocketResponse, queue: Queue[BaseOutEvent]) -> None:
        while True:
            try:
                while True:
                    event = await queue.get()
                    text = event.model_dump_json(by_alias=True, exclude_none=True)
                    if (key := event.event_id) is not None:
                        self._sent_events[key] = event
                    await ws.send_str(text)
                    queue.task_done()
            except Exception as e:  # noqa: PERF203
                self.plugin_connection.process_exception(e, 'Outgoing queue worker')

    async def _websocket_ping(self, ping_interval: float) -> None:
        log = self.plugin_connection.log
        log.debug('Websocket ping task started')

        ping_text: Final = WebsocketHeartbeatEvent(
            type='WebSocketEvent',
            topic='openhab/websocket/heartbeat',
            payload='PING',
        ).model_dump_json(by_alias=True, exclude_none=True)

        stop_reason: str = ''
        msgs_last: frozenset[str] = frozenset()

        try:
            while True:
                await sleep(ping_interval)

                if (ws := self._websocket) is None:
                    stop_reason = ' (is None)'
                    return None
                await ws.send_str(ping_text)

                # Remove stale events where we didn't get an answer
                in_flight = frozenset(self._sent_events)
                if to_remove := msgs_last & in_flight:
                    wl = HABAppWarning(log).add(f'Removing events in flight since {ping_interval}s:')
                    for msg in to_remove:
                        obj = self._sent_events.pop(msg)
                        wl.add(f' - {obj.model_dump_json(by_alias=True, exclude_none=True)}')
                    wl.dump()
                msgs_last = in_flight

        except Exception as e:
            stop_reason = f' {e} ({type(e)})'
            raise
        finally:
            log.debug(f'Websocket ping task stopped{stop_reason:s}')

    async def websockets_task(self) -> None:
        try:
            session = self.plugin_connection.context.session
            token = self._build_token(session.auth)

            ws_cfg = HABApp.CONFIG.openhab.connection.websocket
            max_msg_size = int(ws_cfg.max_msg_size)
            ping_interval = ws_cfg.ping_interval

            async with session.ws_connect(
                    f'/ws?accessToken={token:s}', autoping=False, max_msg_size=max_msg_size) as ws:

                self._websocket = ws
                try:
                    async with TaskGroup() as tg:
                        tg.create_task(self._websocket_sender(ws, self.queue))
                        tg.create_task(self._websocket_ping(ping_interval))
                        tg.create_task(self._websocket_events())
                finally:
                    self._websocket = None

        # TODO: replace this with exception group as soon as 3.14 is available
        except Exception as e:
            self.plugin_connection.process_exception(e, self.websockets_task)

    async def _setup_websocket_filter(self, ws: ClientWebSocketResponse, log: logging.Logger) -> None:
        # setup event type filter
        filter_cfg = HABApp.CONFIG.openhab.connection.websocket.event_filter
        supported_event_names = set(
            get_discriminator_values_from_union(OpenHabEventType, allow_multiple=('WebSocketEvent', ))
        )

        names: set[str] = set()
        if filter_cfg.event_type.is_auto():
            names.update(supported_event_names)

            # We ignore the ItemStateEvent because we will process the ItemStateUpdatedEvent
            # which has the correct value type for the item
            names.discard('ItemStateEvent')

            # https://github.com/spacemanspiff2007/HABApp/issues/437
            # https://github.com/spacemanspiff2007/HABApp/issues/449
            # openHAB will automatically restore the future states of the item
            # which means we can safely ignore these events because we will see the ItemStateUpdatedEvent
            names.discard('ItemTimeSeriesUpdatedEvent')
            names.discard('ItemTimeSeriesEvent')

        elif filter_cfg.event_type.is_config():
            names.update(filter_cfg.types_allowed)
            if invalid := (names - supported_event_names):
                log.warning(
                    f'Invalid event type name{"s" if len(invalid) != 1 else ""} '
                    f'in filter config: {", ".join(sorted(invalid))}')
                names -= invalid

        if names:
            msg = WebsocketSendTypeFilter(payload=sorted(names))
            log.debug(f'Send: {msg.model_dump_json(by_alias=True)}')
            await ws.send_str(msg.model_dump_json(by_alias=True))

        return None

    async def _websocket_events(self) -> None:
        if (ws := self._websocket) is None:
            return None

        # cache so we don't have to look up every event
        _on_openhab_event = on_openhab_event
        log = self.plugin_connection.log
        log_events = logging.getLogger(f'{TOPIC_EVENTS}.openhab')
        debug_lvl = logging.DEBUG

        # Setup event filter
        await self._setup_websocket_filter(ws, log)

        # Websocket constants
        ws_type_text = WSMsgType.TEXT
        ws_type_close = WSMsgType.CLOSED
        topic_heartbeat = WebsocketTopicEnum.HEARTBEAT
        topic_error = WebsocketTopicEnum.REQUEST_FAILED
        topic_success = WebsocketTopicEnum.REQUEST_SUCCESS

        oh_type_adapter = OPENHAB_EVENT_TYPE_ADAPTER

        while True:
            msg = await ws.receive()
            msg_type, data, extra = msg

            if msg_type == ws_type_close:
                log.debug(f'Websocket closed: {ws.close_code} {extra}')
                break

            if msg_type != ws_type_text:
                log.warning(f'Message with unexpected type received: {msg}')
                continue

            if log_events.isEnabledFor(debug_lvl):
                log_events._log(debug_lvl, data, ())

            try:
                oh_event = oh_type_adapter.validate_json(data)
            except ValidationError as e:
                HABAppError(log).add(f'Input: {data:s}').add_exception(e).dump()
                continue

            # Websocket events are not processed by the event bus
            if oh_event.type == 'WebSocketEvent':
                topic = oh_event.topic

                # confirmation that the event was processed
                if topic == topic_success:
                    self._sent_events.pop(oh_event.event_id, None)
                    continue

                # Error processing the sent event
                if topic == topic_error:
                    err_log = HABAppError(log)
                    err_log.add('Request failed!')
                    if (send_obj := self._sent_events.get(oh_event.event_id)) is not None:
                        err_log.add(f'Sent    : {send_obj.model_dump_json(by_alias=True, exclude_none=True):s}')
                    err_log.add(f'Received: {data}').add(f'{oh_event}').dump()
                    self._sent_events.pop(oh_event.event_id, None)
                    continue

                if topic == topic_heartbeat:
                    continue

                log.debug(f'Receive: {data}')
                log.debug(str(oh_event))
                continue

            try:
                event = oh_event.to_event()
            except ValueError as e:
                HABAppError(log).add(f'Input: {data:s}').add(f'{e} ({type(e)}').dump()
                continue

            _on_openhab_event(event)

        # We need to raise an error otherwise the task group will not exit
        raise WebSocketClosedError()
