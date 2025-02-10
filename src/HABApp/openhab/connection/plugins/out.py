from __future__ import annotations

from asyncio import Queue, QueueEmpty, sleep
from typing import TYPE_CHECKING, Any, Final, Literal

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import ItemRegistryItem, uses_get_item
from HABApp.core.lib import SingleTask
from HABApp.core.logger import log_error, log_info, log_warning
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler import convert_to_oh_str, post, put
from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent
from HABApp.openhab.definitions.websockets.item_value_types import RawTypeModel


if TYPE_CHECKING:
    from HABApp.openhab.definitions.websockets.base import BaseOutEvent
    from HABApp.openhab.items import OpenhabItem


get_item = uses_get_item()


def empty_queue(queue: Queue) -> None:
    if queue is not None:
        try:
            while True:
                queue.get_nowait()
        except QueueEmpty:
            pass


class OutgoingCommandsPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)

        self.queue: Queue[BaseOutEvent] | None = None
        self.http_queue: Queue[tuple[str, str, bool]] | None = None

        self.task_http_worker: Final = SingleTask(self.http_queue_worker, 'OhHttpQueueWorker')
        self.task_watcher_websocket: Final = SingleTask(self.websocket_queue_watcher, 'OhWebsocketQueueWatcher')
        self.task_watcher_http: Final = SingleTask(self.http_queue_watcher, 'OhHttpQueueWatcher')

    async def on_connected(self, context: OpenhabContext) -> None:
        self.queue: Queue[BaseOutEvent] = context.out_queue
        self.http_queue: Queue[tuple[str, str, bool]] = Queue()

        self.task_http_worker.start()
        self.task_watcher_http.start()
        self.task_http_worker.start()

    async def on_disconnected(self) -> None:
        queue = self.queue
        self.queue = None
        http_queue = self.http_queue
        self.http_queue = None

        await self.task_http_worker.cancel_wait()
        await self.task_watcher_http.cancel_wait()
        await self.task_http_worker.cancel_wait()

        empty_queue(queue)
        empty_queue(http_queue)

    async def http_queue_worker(self) -> None:

        queue: Final = self.http_queue

        while True:
            try:
                while True:
                    item, state, is_cmd = await queue.get()

                    # this check should never be hit
                    if not isinstance(state, str):
                        log_error(
                            self.plugin_connection.log,
                            f'Ignored invalid state for item {item:s}: "{state}" ({type(state)})'
                        )
                        continue

                    if is_cmd:
                        await post(f'/rest/items/{item:s}', data=state)
                    else:
                        await put(f'/rest/items/{item:s}/state', data=state)
            except Exception as e:  # noqa: PERF203
                self.plugin_connection.process_exception(e, 'Outgoing queue worker')

    def async_post_update(self, item: str | ItemRegistryItem, state: Any) -> None:
        if not isinstance(item, str):
            item = item.name
        if not isinstance(state, str):
            state = convert_to_oh_str(state)
        if (queue := self.http_queue) is None:
            return None
        queue.put_nowait((item, state, False))

    def async_send_command(self, item: str | ItemRegistryItem, state: Any) -> None:
        if not isinstance(item, str):
            item = item.name
        if not isinstance(state, str):
            state = convert_to_oh_str(state)
        if (queue := self.http_queue) is None:
            return None
        queue.put_nowait((item, state, True))

    def async_send_websocket_event(self, event: ItemStateSendEvent | ItemCommandSendEvent) -> None:
        if not isinstance(event, (ItemStateSendEvent, ItemCommandSendEvent)):
            msg = f'Invalid event type: {type(event)}'
            raise TypeError(msg)

        # Workaround for big message sizes
        # https://github.com/openhab/openhab-core/issues/4587
        if isinstance(event.payload, RawTypeModel):
            if (http_queue := self.http_queue) is None:
                return None
            # 'openhab/items/<NAME>/<state|command>'
            _, _, name, action = event.topic.split('/')
            http_queue.put_nowait((name, event.payload.value, action == 'command'))
            return None

        if (queue := self.queue) is None:
            return None
        queue.put_nowait(event)

    async def websocket_queue_watcher(self) -> None:
        await self._queue_watcher(self.queue, 'websocket')

    async def http_queue_watcher(self) -> None:
        await self._queue_watcher(self.http_queue, 'http')

    async def _queue_watcher(self, queue: Queue, name: str) -> None:
        log = self.plugin_connection.log
        first_msg_at = 150

        upper = first_msg_at
        lower = -1
        last_info_at = first_msg_at // 2

        while True:
            await sleep(10)
            size = queue.qsize()

            # small log msg
            if size > upper:
                upper = size * 2
                lower = size // 2
                log_warning(log, f'{size} messages in {name:s} queue')
            elif size < lower:
                upper = max(size / 2, first_msg_at)
                lower = size // 2
                if lower <= last_info_at:
                    lower = -1
                    log_info(log, 'queue OK')
                else:
                    log_info(log, f'{size} messages in {name:s} queue')


OUTGOING_PLUGIN: Final = OutgoingCommandsPlugin()
async_post_update: Final = OUTGOING_PLUGIN.async_post_update
async_send_command: Final = OUTGOING_PLUGIN.async_send_command
async_send_websocket_event: Final = OUTGOING_PLUGIN.async_send_websocket_event


def send_websocket_event(event: ItemStateSendEvent | ItemCommandSendEvent) -> None:
    return run_func_from_async(async_send_websocket_event, event)


def try_get_item(item: str | ItemRegistryItem) -> OpenhabItem | None:
    item_name = item.name if isinstance(item, ItemRegistryItem) else item

    if not isinstance(item_name, str):
        msg = f'Invalid item type: {type(item)}'
        raise TypeError(msg)

    try:
        item = get_item(item_name)
    except ItemNotFoundException:
        return None

    return item


def post_update(item: str | ItemRegistryItem, state: Any, *,
                transport: Literal['http', 'websocket'] = 'websocket') -> None:
    """
    Post an update to the item

    :param item: item name or item
    :param state: new item state
    :param transport: transport to use. Websocket is much faster but stricter concerning which types are accepted
    """

    # by default, we use the websocket connection because it's much faster
    if transport != 'websocket' or (item_obj := try_get_item(item)) is None:
        return run_func_from_async(async_post_update, item, state)

    return item_obj.oh_post_update(state)


def send_command(item: str | ItemRegistryItem, command: Any, *,
                transport: Literal['http', 'websocket'] = 'websocket') -> None:
    """
    Send the specified command to the item

    :param item: item name or item
    :param command: command
    :param transport: transport to use. Websocket is much faster but stricter concerning which types are accepted
    """

    # by default, we use the websocket connection because it's much faster
    if transport != 'websocket' or (item_obj := try_get_item(item)) is None:
        return run_func_from_async(async_send_command, item, command)

    return item_obj.send_command(command)
