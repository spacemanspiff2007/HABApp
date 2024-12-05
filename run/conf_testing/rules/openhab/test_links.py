from HABAppTests import TestBaseRule

from HABApp.openhab.connection.handler.func_async import async_get_link, async_get_links


class OpenhabLinkApi(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()
        self.add_test('AllLinks', self.api_get_links)

    async def api_get_links(self) -> None:
        objs = await async_get_links()
        assert objs

        obj = objs[0]

        single = await async_get_link(obj.item, obj.channel)
        assert single == obj


OpenhabLinkApi()
