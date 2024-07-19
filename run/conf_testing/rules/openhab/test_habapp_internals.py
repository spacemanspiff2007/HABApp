from HABAppTests import OpenhabTmpItem, TestBaseRule, run_coro

from HABApp.openhab.connection.handler.func_async import (
    async_get_item_with_habapp_meta,
    async_remove_habapp_metadata,
    async_set_habapp_metadata,
)
from HABApp.openhab.definitions.rest.habapp_data import HABAppThingPluginData


class OpenhabMetaData(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('async', self.create_meta)

    def create_meta(self):
        with OpenhabTmpItem('String') as tmpitem:
            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            assert d.metadata['HABApp'] is None

            # create empty set
            run_coro(async_set_habapp_metadata(tmpitem.name, HABAppThingPluginData()))

            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            assert isinstance(d.metadata['HABApp'], HABAppThingPluginData)

            # create valid data
            run_coro(async_set_habapp_metadata(
                tmpitem.name, HABAppThingPluginData(created_link='asdf', created_ns=['a', 'b']))
            )

            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            d = d.metadata['HABApp']
            assert isinstance(d, HABAppThingPluginData)
            assert d.created_link == 'asdf'
            assert d.created_ns == ['a', 'b']

            # remove metadata again
            run_coro(async_remove_habapp_metadata(tmpitem.name))
            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            assert d.metadata['HABApp'] is None


OpenhabMetaData()
