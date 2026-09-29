from HABAppTests import AsyncOpenhabTmpItem, TestBaseRule


class OpenhabMetaData(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()
        self.add_test('create_metadata', self.create_meta)

    @AsyncOpenhabTmpItem.create('String', arg_name='tmpitem')
    async def create_meta(self, tmpitem: AsyncOpenhabTmpItem) -> None:

        d = await self.async_oh.get_item(tmpitem.name)
        assert 'HABApp' not in d.metadata

        # create metadata
        await self.async_oh.set_metadata(tmpitem.name, 'HABApp', 'value', {'a': 'b'})

        d = await self.async_oh.get_item(tmpitem.name)
        assert d.metadata['HABApp'] == {'value': 'value', 'config': {'a': 'b'}, 'editable': True}

        # remove metadata again
        await self.async_oh.remove_metadata(tmpitem.name, 'HABApp')
        d = await self.async_oh.get_item(tmpitem.name)
        assert 'HABApp' not in d.metadata


OpenhabMetaData()
