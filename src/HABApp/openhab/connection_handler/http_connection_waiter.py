import asyncio
import time


MAX_WAIT: int = 180


class WaitBetweenConnects:
    def __init__(self):
        self.last_try: float = 0
        self.wait_time = 0

    async def wait(self):

        # wenn wir lang connected sind oder beim ersten mal versuchen wir den reconnect gleich
        if time.time() - self.last_try > MAX_WAIT:
            wait = 0
        else:
            wait = self.wait_time
            wait = wait * 2 if wait <= 16 else wait + 8
            wait = max(wait, 1)
            wait = min(wait, MAX_WAIT)

        self.wait_time = wait
        await asyncio.sleep(self.wait_time)

        self.last_try = time.time()
