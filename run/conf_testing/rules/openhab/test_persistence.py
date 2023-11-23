from __future__ import annotations

from datetime import datetime, timedelta
from typing import Final, Any

from HABApp.openhab.definitions.helpers import OpenhabPersistenceData
from HABApp.openhab.items import NumberItem
from HABAppTests import TestBaseRule


class TestPersistenceBase(TestBaseRule):
    def __init__(self, service_name: str, item_name: str):
        super().__init__()

        self.config.skip_on_failure = True
        self.item_name: Final = item_name
        self.service_name: Final = service_name

        self.add_test(f'Persistence {service_name} available', self.test_service_available)

    def set_up(self):
        i = NumberItem.get_item(self.item_name)
        i.oh_post_update(int(i.value) + 1 if i.value < 10 else 0)

    def test_service_available(self):
        for cfg in self.oh.get_persistence_services():
            if cfg.id == self.service_name:
                break
        else:
            raise ValueError(f'Persistence service "{self.service_name}" not found!')

    def set_persistence_data(self, time: datetime, state: Any):
        return self.openhab.set_persistence_data(self.item_name, self.service_name, time, state)

    def get_persistence_data(self, start_time: datetime | None, end_time: datetime | None) -> OpenhabPersistenceData:
        return self.openhab.get_persistence_data(self.item_name, self.service_name, start_time, end_time)


class TestRRD4j(TestPersistenceBase):

    def __init__(self):
        super().__init__('rrd4j', 'RRD4J_Item')
        self.add_test('RRD4J get', self.test_get)

    def test_get(self):
        now = datetime.now()
        d = self.get_persistence_data(now - timedelta(seconds=60), now)
        assert d.get_data()


TestRRD4j()


class TestMapDB(TestPersistenceBase):

    def __init__(self):
        super().__init__('mapdb', 'RRD4J_Item')
        self.add_test('MapDB get', self.test_get)

    def test_get(self):
        now = datetime.now()
        d = self.get_persistence_data(now - timedelta(seconds=60), now)
        assert d.get_data()


TestMapDB()
