from __future__ import annotations

from asyncio import Queue, QueueEmpty, sleep
from typing import Any, Final

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import ItemRegistryItem
from HABApp.core.lib import SingleTask
from HABApp.core.logger import log_error, log_info, log_warning
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler import convert_to_oh_type, post, put


class OutgoingCommandsPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)

        self.queue: Queue[tuple[str, str, bool]] | None = None
        self.task_worker: Final = SingleTask(self.queue_worker, 'OhQueueWorker')
        self.task_watcher: Final = SingleTask(self.queue_watcher, 'OhQueueWatcher')

    @staticmethod
    def _clear_queue(queue: Queue | None) -> None:
        if queue is None:
            return None

        try:
            while True:
                queue.get_nowait()
        except QueueEmpty:
            pass

    async def on_connected(self, context: OpenhabContext) -> None:
        self.queue = context.out_queue
        self.task_worker.start()
        self.task_watcher.start()

    async def on_disconnected(self, context: OpenhabContext) -> None:
        queue = self.queue
        self.queue = None

        await self.task_worker.cancel_wait()
        await self.task_watcher.cancel_wait()
        self._clear_queue(queue)

    async def queue_watcher(self) -> None:
        queue: Final = self.queue
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
                log_warning(log, f'{size} messages in queue')
            elif size < lower:
                upper = max(size / 2, first_msg_at)
                lower = size // 2
                if lower <= last_info_at:
                    lower = -1
                    log_info(log, 'queue OK')
                else:
                    log_info(log, f'{size} messages in queue')

    # noinspection PyProtectedMember
    async def queue_worker(self) -> None:

        queue: Final = self.queue

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
            state = convert_to_oh_type(state)
        if (queue := self.queue) is None:
            return None
        queue.put_nowait((item, state, False))

    def async_send_command(self, item: str | ItemRegistryItem, state: Any) -> None:
        if not isinstance(item, str):
            item = item.name
        if not isinstance(state, str):
            state = convert_to_oh_type(state)
        if (queue := self.queue) is None:
            return None
        queue.put_nowait((item, state, True))


OUTGOING_PLUGIN: Final = OutgoingCommandsPlugin()
async_post_update: Final = OUTGOING_PLUGIN.async_post_update
async_send_command: Final = OUTGOING_PLUGIN.async_send_command


def post_update(item: str | ItemRegistryItem, state: Any) -> None:
    """
    Post an update to the item

    :param item: item name or item
    :param state: new item state
    """
    if not isinstance(item, (str, ItemRegistryItem)):
        msg = f'Invalid item type: {type(item)}'
        raise TypeError(msg)

    return run_func_from_async(async_post_update, item, state)


def send_command(item: str | ItemRegistryItem, command: Any) -> None:
    """
    Send the specified command to the item

    :param item: item name or item
    :param command: command
    """
    if not isinstance(item, (str, ItemRegistryItem)):
        msg = f'Invalid item type: {type(item)}'
        raise TypeError(msg)

    return run_func_from_async(async_send_command, item, command)
