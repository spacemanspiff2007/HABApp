import asyncio

import HABApp


class AsyncRule(HABApp.Rule):

    def __init__(self):
        super().__init__()

        self.run_soon(self.async_func)

    async def async_func(self):
        await asyncio.sleep(2)
        async with self.async_http.get('http://httpbin.org/get') as resp:
            print(resp)
            print(await resp.text())


AsyncRule()
