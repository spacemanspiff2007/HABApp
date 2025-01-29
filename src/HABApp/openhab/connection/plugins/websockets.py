from __future__ import annotations

import logging
from asyncio import TaskGroup, sleep
from base64 import b64encode
from inspect import isclass
from typing import Annotated, Final, get_args, get_origin

from aiohttp import BasicAuth, ClientError, ClientWebSocketResponse, WSMsgType
from pydantic import ValidationError

import HABApp
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.const.json import dump_json
from HABApp.core.const.log import TOPIC_EVENTS
from HABApp.core.internals import uses_item_registry
from HABApp.core.lib import SingleTask
from HABApp.core.logger import HABAppError
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.definitions.websockets import (
    OPENHAB_EVENT_TYPE,
    OPENHAB_EVENT_TYPE_ADAPTER,
    WebsocketSendTypeFilter,
    WebsocketTopicEnum,
)
from HABApp.openhab.definitions.websockets.base import BaseModel
from HABApp.openhab.process_events import on_openhab_event


class WebSocketClosedError(ClientError):
    pass


Items = uses_item_registry()


class WebsocketPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.task: Final = SingleTask(self.websockets_task, name='WebsocketsEventsTask')

        self._websocket: ClientWebSocketResponse | None = None

    async def on_connected(self) -> None:
        self.task.start()

    async def on_disconnected(self) -> None:
        await self.task.cancel_wait()

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

    async def _websocket_ping(self, ping_interval: float) -> None:
        log = self.plugin_connection.log
        log.debug('Websocket ping task started')

        ping_text = dump_json({
            'type': 'WebSocketEvent',
            'topic': 'openhab/websocket/heartbeat',
            'payload': 'PING',
            'source': 'HABApp',
        })

        reason: str = ''

        try:
            while True:
                await sleep(ping_interval)

                if (ws := self._websocket) is None:
                    reason = ' (is None)'
                    return None
                await ws.send_str(ping_text)
        except Exception as e:
            reason = f' {e} ({type(e)})'
            raise
        finally:
            log.debug(f'Websocket ping task stopped{reason:s}')

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
                        tg.create_task(self._websocket_ping(ping_interval))
                        tg.create_task(self._websocket_events())
                finally:
                    self._websocket = None

        except Exception as e:
            self.plugin_connection.process_exception(e, self.websockets_task)

    @staticmethod
    def _get_type_names_from_adapter() -> list[str]:
        names = set()

        objs = [get_args(OPENHAB_EVENT_TYPE)[0]]

        while objs:
            obj = objs.pop(0)

            if isclass(obj) and issubclass(obj, BaseModel):
                literal = obj.model_fields['type'].annotation
                literal_value = get_args(literal)
                if len(literal_value) != 1:
                    msg = f'Expected exactly one literal value for {literal!r}'
                    raise ValueError(msg)
                names.add(literal_value[0])
                continue

            if get_origin(obj) is Annotated:
                objs.append(get_args(obj)[0])
                continue

            new = get_args(obj)
            if not new:
                msg = f'Expected args for {obj!r}'
                raise ValueError(msg)
            objs.extend(new)

        return sorted(names)

    async def _setup_websocket_filter(self, ws: ClientWebSocketResponse, log: logging.Logger) -> None:
        # setup event type filter
        filter_cfg = HABApp.CONFIG.openhab.connection.websocket.event_filter
        supported_event_names = set(self._get_type_names_from_adapter())

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
        DEBUG = logging.DEBUG

        # Setup event filter
        await self._setup_websocket_filter(ws, log)

        # Websocket constants
        ws_type_text = WSMsgType.TEXT
        topic_heartbeat = WebsocketTopicEnum.HEARTBEAT
        topic_error = WebsocketTopicEnum.REQUEST_FAILED

        async for msg in ws:
            msg_type, data, extra = msg

            if msg_type != ws_type_text:
                log.warning(f'Message with unexpected type received: {msg}')
                continue

            if log_events.isEnabledFor(DEBUG):
                log_events._log(DEBUG, data, ())

            try:
                oh_event = OPENHAB_EVENT_TYPE_ADAPTER.validate_json(data)
            except ValidationError as e:
                HABAppError(log).add(f'Input: {data:s}').add_exception(e).dump()
                continue

            # Websocket events are not processed by the event bus
            if oh_event.type == 'WebSocketEvent':
                if oh_event.topic == topic_heartbeat:
                    continue
                if oh_event.type == topic_error:
                    continue
                log.debug(f'Receive: {data}')
                log.debug(str(oh_event))
                continue

            event = oh_event.to_event()
            _on_openhab_event(event)

        # We need to raise an error otherwise the task group will not exit
        raise WebSocketClosedError()
