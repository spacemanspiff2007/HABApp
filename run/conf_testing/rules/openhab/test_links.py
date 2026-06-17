from HABAppTests import TestBaseRule


class OpenhabLinkApi(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()
        self.add_test('AllLinks', self.api_get_links)

    async def api_get_links(self) -> None:
        objs = await self.async_oh.get_links()
        assert objs

        obj = objs[0]

        single = await self.async_oh.get_link(obj.item, obj.channel)
        assert single == obj


OpenhabLinkApi()
