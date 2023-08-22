from asyncio import sleep, Task, create_task, CancelledError
from typing import Optional

from HABApp.core.connections import BaseConnection, BaseConnectionPlugin


class WaitBetweenConnects:
    wait_max = 600

    def __init__(self):
        self.wait_time: int = 0
        self.task: Optional[Task] = None

    def reset_wait(self):
        self.wait_time = 0

    async def wait(self):
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

    def cancel(self):
        if task := self.task:
            task.cancel()


class AutoReconnectPlugin(BaseConnectionPlugin):
    def __init__(self):
        super().__init__(priority=-110_000)
        self.waiter = WaitBetweenConnects()

    def application_shutdown(self):
        self.waiter.cancel()

    async def on_online(self):
        self.waiter.reset_wait()

    async def on_offline(self, connection: BaseConnection):
        if connection.is_shutdown:
            return None

        if connection.has_errors:
            await self.waiter.wait()
            connection.clear_error()
