from datetime import datetime, timedelta

from HABApp.openhab.items import NumberItem
from HABAppTests import TestBaseRule


class TestPersistence(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.item = 'RRD4J_Item'

        self.add_test('RRD4J configured', self.test_configured)
        self.add_test('RRD4J get', self.test_get)

    def set_up(self):
        i = NumberItem.get_item(self.item)
        i.oh_post_update(i.value + 1 if i.value < 10 else 0)

    def test_configured(self):
        for cfg in self.oh.get_persistence_services():
            if cfg.id == 'rrd4j':
                break
        else:
            raise ValueError('rrd4j not found!')

    def test_get(self):
        now = datetime.now()
        d = self.openhab.get_persistence_data(self.item, 'rrd4j', now - timedelta(seconds=60), now)
        assert d.get_data()

    # def test_set(self):
    #     now = datetime.now()
    #     d = self.openhab.get_persistence_data(self.item, 'mapdb', now - timedelta(seconds=5), now)
    #     was = d.get_data()
    #
    #     assert list(was.values()) == [1]
    #
    #     self.openhab.set_persistence_data(self.item, 'mapdb', now, 2)
    #
    #     d = self.openhab.get_persistence_data(self.item, 'mapdb', now - timedelta(seconds=5),
    #                                           now + timedelta(seconds=5))
    #     ist = d.get_data()
    #     assert list(ist.values()) == [2], ist


TestPersistence()
