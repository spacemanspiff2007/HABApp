from HABAppTests import AsyncOpenhabTmpItem, TestBaseRule

from HABApp.openhab.connection.handler.func_async import (
    async_get_item_with_habapp_meta,
    async_remove_habapp_metadata,
    async_set_habapp_metadata,
)
from HABApp.openhab.definitions.rest.habapp_data import HABAppThingPluginData


class OpenhabMetaData(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()
        self.add_test('async', self.create_meta)

    @AsyncOpenhabTmpItem.create('String', arg_name='tmpitem')
    async def create_meta(self, tmpitem: AsyncOpenhabTmpItem) -> None:
            d = await async_get_item_with_habapp_meta(tmpitem.name)
            assert d.metadata['HABApp'] is None

            # create empty set
            await async_set_habapp_metadata(tmpitem.name, HABAppThingPluginData())

            d = await async_get_item_with_habapp_meta(tmpitem.name)
            assert isinstance(d.metadata['HABApp'], HABAppThingPluginData)

            # create valid data
            await async_set_habapp_metadata(
                tmpitem.name, HABAppThingPluginData(created_link='asdf', created_ns=['a', 'b'])
            )

            d = await async_get_item_with_habapp_meta(tmpitem.name)
            d = d.metadata['HABApp']
            assert isinstance(d, HABAppThingPluginData)
            assert d.created_link == 'asdf'
            assert d.created_ns == ['a', 'b']

            # remove metadata again
            await async_remove_habapp_metadata(tmpitem.name)
            d = await async_get_item_with_habapp_meta(tmpitem.name)
            assert d.metadata['HABApp'] is None


OpenhabMetaData()
