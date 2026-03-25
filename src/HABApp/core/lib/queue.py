import asyncio
from asyncio import Future, QueueEmpty
from collections import deque
from typing import Final


class SingleConsumerQueue[T]:
    __slots__ = ('_getter', '_is_open', '_loop', '_queue')

    def __init__(self) -> None:
        super().__init__()
        self._loop: Final = asyncio.get_running_loop()
        self._queue: Final[deque[T]] = deque()

        self._is_open: bool = True
        self._getter: Future[None] | None = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(is_open={self._is_open}, queue_size={len(self._queue)})'

    def __len__(self) -> int:
        return len(self._queue)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def set_open(self, is_open: bool) -> None:  # noqa: FBT001
        self._is_open = is_open

        if not is_open:
            self._queue.clear()
        return None

    async def get(self) -> T:
        while not self._queue:
            if self._getter is not None:
                msg = 'Only one consumer allowed'
                raise RuntimeError(msg)

            self._getter = getter = self._loop.create_future()
            try:
                await getter
            finally:
                self._getter = None

        return self.get_nowait()

    def get_nowait(self) -> T:
        if not self._queue:
            raise QueueEmpty
        return self._queue.popleft()

    def put_nowait(self, item: T) -> None:
        if not self._is_open:
            return None

        self._queue.append(item)

        # wake up getter, but only if it is waiting
        if (g := self._getter) is not None and not g.done():
            g.set_result(None)
        return None
