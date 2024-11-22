import asyncio

import HABApp


class AsyncRule(HABApp.Rule):

    def __init__(self) -> None:
        super().__init__()

        self.run.soon(self.async_func)

    async def async_func(self) -> None:
        await asyncio.sleep(2)
        async with self.async_http.get('http://httpbin.org/get') as resp:
            print(resp)
            print(await resp.text())


AsyncRule()
