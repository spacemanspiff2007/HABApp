from HABApp.openhab.connection_handler.func_async import async_get_item_with_habapp_meta, async_set_habapp_metadata, \
    async_remove_habapp_metadata
from HABApp.openhab.definitions.rest.habapp_data import HABAppThingPluginData
from HABApp.openhab.events import ItemUpdatedEvent
from HABApp.openhab.interface import create_item
from HABApp.openhab.items import StringItem, NumberItem, DatetimeItem
from HABAppTests import TestBaseRule, OpenhabTmpItem, run_coro, EventWaiter


class TestMetadata(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('create meta', self.create_meta)

    def create_meta(self):
        with OpenhabTmpItem(None, 'String') as tmpitem:
            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            assert d['metadata']['HABApp'] is None

            # create empty set
            run_coro(async_set_habapp_metadata(tmpitem.name, HABAppThingPluginData()))

            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            assert isinstance(d['metadata']['HABApp'], HABAppThingPluginData)


            # create valid data
            run_coro(async_set_habapp_metadata(
                tmpitem.name, HABAppThingPluginData(created_link='asdf', created_ns=['a', 'b']))
            )

            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            d = d['metadata']['HABApp']
            assert isinstance(d, HABAppThingPluginData)
            assert d.created_link == 'asdf'
            assert d.created_ns == ['a', 'b']

            # remove metadata again
            run_coro(async_remove_habapp_metadata(tmpitem.name))
            d = run_coro(async_get_item_with_habapp_meta(tmpitem.name))
            assert d['metadata']['HABApp'] is None

        return True


TestMetadata()


class ChangeItemType(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('change_item', self.change_item)

    def change_item(self):
        with OpenhabTmpItem(None, 'Number') as tmpitem:
            NumberItem.get_item(tmpitem.name)

            create_item('String', tmpitem.name)
            EventWaiter(tmpitem.name, ItemUpdatedEvent(tmpitem.name, 'String'), 2, False)
            StringItem.get_item(tmpitem.name)

            create_item('DateTime', tmpitem.name)
            EventWaiter(tmpitem.name, ItemUpdatedEvent(tmpitem.name, 'DateTime'), 2, False)
            DatetimeItem.get_item(tmpitem.name)


ChangeItemType()
