from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import ItemRegistryItem
from HABApp.core.lib import SingleTask
from HABApp.core.logger import log_error
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler import convert_to_oh_type, post, put


if TYPE_CHECKING:
    from asyncio import Queue


class OutgoingCommandsPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)

        self.queue: Queue[tuple[str, str, bool]] | None = None
        self.task_worker: Final = SingleTask(self.queue_worker, 'OhQueueWorker')

    async def on_connected(self, context: OpenhabContext) -> None:
        self.queue = context.out_queue
        self.task_worker.start()

    async def on_disconnected(self) -> None:
        self.queue = None
        await self.task_worker.cancel_wait()

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
