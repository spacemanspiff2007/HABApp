from datetime import datetime, timedelta

from HABApp.openhab.items import NumberItem
from HABAppTests import TestBaseRule


class TestPersistence(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.item = 'MapDBItem'

        self.add_test('Persistence MapDB get', self.test_get)
        self.add_test('Persistence MapDB set', self.test_set)

    def set_up(self):
        NumberItem.get_item(self.item).oh_post_update('1')

    def test_get(self):
        now = datetime.now()
        d = self.openhab.get_persistence_data(self.item, 'mapdb', now - timedelta(seconds=5), now)
        assert d.get_data()

    def test_set(self):
        now = datetime.now()
        d = self.openhab.get_persistence_data(self.item, 'mapdb', now - timedelta(seconds=5), now)
        was = d.get_data()

        assert list(was.values()) == [1]

        self.openhab.set_persistence_data(self.item, 'mapdb', now, 2)

        d = self.openhab.get_persistence_data(self.item, 'mapdb', now - timedelta(seconds=5),
                                              now + timedelta(seconds=5))
        ist = d.get_data()
        assert list(ist.values()) == [2], ist


TestPersistence()
