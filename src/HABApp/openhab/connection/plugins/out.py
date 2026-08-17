from __future__ import annotations

from typing import TYPE_CHECKING, Final

from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.logger import log_error
from HABApp.openhab.connection.connection import OhHttpQueue, OpenhabConnection


if TYPE_CHECKING:
    from HABApp.config.models.openhab import General as OhGeneralConfig
    from HABApp.core.lib.asyncio import AsyncioProvider
    from HABApp.openhab.connection.handler import OhClientSession


class OutgoingCommandsPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None, *,
                 asyncio_provider: AsyncioProvider, http_queue: OhHttpQueue, oh_connection: OhClientSession,
                 config: OhGeneralConfig) -> None:
        super().__init__(name)

        self.http_queue: Final[OhHttpQueue] = http_queue
        self.task_http_worker: Final = asyncio_provider.create_single_task(
            self.http_queue_worker, 'OhHttpQueueWorker'
        )
        self._oh: Final = oh_connection
        self._cfg: Final = config

    def cfg_updated(self) -> None:
        self.http_queue.set_open(not self._cfg.listen_only)

    async def on_connected(self) -> None:
        self.cfg_updated()  # open the queue if we are not read only

        self.task_http_worker.start()

    async def on_disconnected(self) -> None:
        self.http_queue.set_open(False)     # Always close queue unconditionally

        await self.task_http_worker.cancel_wait()

    async def http_queue_worker(self) -> None:

        queue: Final = self.http_queue
        post: Final = self._oh.post
        put: Final = self._oh.put

        while True:
            try:
                while True:
                    item, state, is_cmd, source = await queue.get()

                    # this check should never be hit
                    if not isinstance(state, str):
                        log_error(
                            self.plugin_connection.log,
                            f'Ignored invalid state for item {item:s}: "{state}" ({type(state)})'
                        )
                        continue

                    src = 'HABApp' if source is None else f'HABApp.{source:s}'

                    if is_cmd:
                        await post(f'/rest/items/{item:s}', data=state, params=(('source', src), ))
                    else:
                        await put(f'/rest/items/{item:s}/state', data=state, params=(('source', src), ))
            except Exception as e:  # noqa: PERF203
                self.plugin_connection.process_exception(e, 'Outgoing queue worker')
