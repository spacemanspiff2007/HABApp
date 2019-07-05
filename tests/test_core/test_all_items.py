import unittest

from HABApp.core.items import Item
from HABApp.core import Items


class TestCasesItem(unittest.TestCase):

    def tearDown(self) -> None:
        for name in Items.get_item_names():
            Items.pop_item(name)

    def setUp(self) -> None:
        for name in Items.get_item_names():
            Items.pop_item(name)

    def test_item(self):

        NAME = 'test'
        created_item = Item(NAME)
        Items.set_item(created_item)

        self.assertTrue(Items.item_exists(NAME))
        self.assertIs(created_item, Items.get_item(NAME))

        self.assertEqual(Items.get_item_names(), [NAME])
        self.assertEqual(Items.get_all_items(), [created_item])

        self.assertIs(created_item, Items.pop_item(NAME))
        self.assertEqual(Items.get_all_items(), [])


if __name__ == '__main__':
    unittest.main()
