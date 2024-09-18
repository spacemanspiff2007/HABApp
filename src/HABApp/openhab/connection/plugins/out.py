from __future__ import annotations

from asyncio import Queue, QueueEmpty, sleep
from typing import Any, Final

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import ItemRegistryItem
from HABApp.core.lib import SingleTask
from HABApp.core.logger import log_info, log_warning
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.connection.handler import convert_to_oh_type, post, put


class OutgoingCommandsPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)

        self.add: bool = False

        self.queue: Queue[tuple[str | ItemRegistryItem, Any, bool]] = Queue()
        self.task_worker: Final = SingleTask(self.queue_worker, 'OhQueueWorker')
        self.task_watcher: Final = SingleTask(self.queue_watcher, 'OhQueueWatcher')

    async def _clear_queue(self) -> None:
        try:
            while True:
                self.queue.get_nowait()
        except QueueEmpty:
            pass

    async def on_connected(self) -> None:
        self.add = True
        self.task_worker.start()
        self.task_watcher.start()

    async def on_disconnected(self) -> None:
        self.add = False
        await self.task_worker.cancel_wait()
        await self.task_watcher.cancel_wait()
        await self._clear_queue()

    async def queue_watcher(self) -> None:
        log = self.plugin_connection.log
        first_msg_at = 150

        upper = first_msg_at
        lower = -1
        last_info_at = first_msg_at // 2

        while True:
            await sleep(10)
            size = self.queue.qsize()

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
        to_str: Final = convert_to_oh_type

        scientific_floats = self.plugin_connection.context.is_oh41

        while True:
            try:
                while True:
                    item, state, is_cmd = await queue.get()

                    if not isinstance(item, str):
                        item = item._name

                    if not isinstance(state, str):
                        state = to_str(state, scientific_floats=scientific_floats)

                    if is_cmd:
                        await post(f'/rest/items/{item:s}', data=state)
                    else:
                        await put(f'/rest/items/{item:s}/state', data=state)
            except Exception as e:  # noqa: PERF203
                self.plugin_connection.process_exception(e, 'Outgoing queue worker')

    def async_post_update(self, item: str | ItemRegistryItem, state: Any):
        if not self.add:
            return None
        self.queue.put_nowait((item, state, False))

    def async_send_command(self, item: str | ItemRegistryItem, state: Any):
        if not self.add:
            return None
        self.queue.put_nowait((item, state, True))


OUTGOING_PLUGIN: Final = OutgoingCommandsPlugin()
async_post_update: Final = OUTGOING_PLUGIN.async_post_update
async_send_command: Final = OUTGOING_PLUGIN.async_send_command


def post_update(item: str | ItemRegistryItem, state: Any) -> None:
    """
    Post an update to the item

    :param item: item name or item
    :param state: new item state
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)

    run_func_from_async(async_post_update, item, state)


def send_command(item: str | ItemRegistryItem, command: Any) -> None:
    """
    Send the specified command to the item

    :param item: item name or item
    :param command: command
    """
    assert isinstance(item, (str, ItemRegistryItem)), type(item)

    run_func_from_async(async_send_command, item, command)
