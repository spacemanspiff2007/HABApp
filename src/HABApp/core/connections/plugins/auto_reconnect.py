from __future__ import annotations

from asyncio import CancelledError, Task, create_task, sleep

from HABApp.core.connections import BaseConnection, BaseConnectionPlugin


class WaitBetweenConnects:
    wait_max = 600

    def __init__(self) -> None:
        self.wait_time: int = 0
        self.task: Task | None = None

    def reset_wait(self) -> None:
        self.wait_time = 0

    async def wait(self) -> None:
        wait = self.wait_time
        wait = wait * 2 if wait <= 16 else wait * 1.5
        wait = max(1, min(wait, self.wait_max))

        self.wait_time = wait

        try:
            self.task = create_task(sleep(self.wait_time))
            await self.task
        except CancelledError:
            pass
        finally:
            self.task = None

    def cancel(self) -> None:
        if task := self.task:
            task.cancel()


class AutoReconnectPlugin(BaseConnectionPlugin):
    _DEFAULT_PRIORITY = 110_000

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.waiter = WaitBetweenConnects()

    def on_application_shutdown(self) -> None:
        self.waiter.cancel()

    async def on_online(self) -> None:
        self.waiter.reset_wait()

    async def on_offline(self, connection: BaseConnection):
        if connection.is_shutdown:
            return None

        if connection.has_errors:
            await self.waiter.wait()
            connection.clear_error()
