import typing
from datetime import datetime, timedelta

from HABApp.core import Items
from HABApp.core.items import Item


class ItemTests:
    CLS: typing.Type[Item] = None
    TEST_VALUES = []
    TEST_CREATE_ITEM = {}

    def test_test_params(self):
        assert self.CLS is not None
        assert self.TEST_VALUES, type(self)

    def test_factories(self):
        cls = self.CLS

        ITEM_NAME = 'testitem'
        if Items.item_exists(ITEM_NAME):
            Items.pop_item(ITEM_NAME)

        c = cls.get_create_item(name=ITEM_NAME, **self.TEST_CREATE_ITEM)
        assert isinstance(c, cls)

        assert isinstance(cls.get_item(name=ITEM_NAME), cls)


    def test_var_names(self):
        item = self.CLS('test')
        # assert item.value is None, f'{item.value} ({type(item.value)})'

        item.set_value(self.TEST_VALUES[0])
        assert item.value == self.TEST_VALUES[0]

        item.post_value(self.TEST_VALUES[0])
        item.get_value(default_value='asdf')

    def test_time_value_update(self):
        for value in self.TEST_VALUES:
            i = self.CLS('test')
            i.set_value(value)
            i.last_change = datetime.now() - timedelta(seconds=5)
            i.last_update = datetime.now() - timedelta(seconds=5)
            i.set_value(value)

            assert i.last_update > datetime.now() - timedelta(milliseconds=100)
            assert i.last_change < datetime.now() - timedelta(milliseconds=100)

    def test_time_value_change(self):
        i = self.CLS('test')
        for value in self.TEST_VALUES:
            i.last_change = datetime.now() - timedelta(seconds=5)
            i.last_update = datetime.now() - timedelta(seconds=5)
            i.set_value(value)

            assert i.last_update > datetime.now() - timedelta(milliseconds=100)
            assert i.last_change > datetime.now() - timedelta(milliseconds=100)
