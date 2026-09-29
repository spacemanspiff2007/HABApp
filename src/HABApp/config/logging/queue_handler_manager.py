from collections.abc import Iterable
from types import TracebackType
from typing import Self

from HABApp.config.logging.queue_handler import HABAppQueueHandler, log
from HABApp.core.provider import HABAPP_PROVIDER


@HABAPP_PROVIDER.register
class LogQueueManager:
    def __init__(self) -> None:
        self.queues: tuple[HABAppQueueHandler, ...] = ()

    def add(self, handlers: Iterable[HABAppQueueHandler]) -> None:
        for handler in handlers:
            self.queues += (handler,)
            handler.start()

    def stop(self) -> None:
        log.debug('Stopping logging queue handlers')

        for qh in self.queues:
            qh.signal_stop()
        while self.queues:
            qh = self.queues[0]
            self.queues = self.queues[1:]
            qh.stop()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> bool:
        self.stop()
