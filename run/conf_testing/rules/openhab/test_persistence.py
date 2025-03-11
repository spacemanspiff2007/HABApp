from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Final

from HABAppTests import ItemWaiter, TestBaseRule

from HABApp.core.connections import Connections
from HABApp.openhab.items import NumberItem


if TYPE_CHECKING:
    from HABApp.openhab.definitions.helpers import OpenhabPersistenceData


class TestPersistenceBase(TestBaseRule):
    def __init__(self, service_name: str, item_name: str) -> None:
        super().__init__()

        self.config.skip_on_failure = True
        self.item_name: Final = item_name
        self.service_name: Final = service_name

        self.add_test(f'Persistence {service_name} available', self.test_service_available)

    def set_up(self) -> None:
        i = NumberItem.get_item(self.item_name)
        if i.value is None:
            i.oh_post_update(0)
            ItemWaiter(self.item_name).wait_for_state(0)
        i.oh_post_update(int(i.value) + 1 if i.value < 10 else 0)

    def test_service_available(self):
        for cfg in self.oh.get_persistence_services():
            if cfg.id == self.service_name:
                break
        else:
            msg = f'Persistence service "{self.service_name}" not found!'
            raise ValueError(msg)

    def set_persistence_data(self, time: datetime, state: Any):
        return self.openhab.set_persistence_data(self.item_name, self.service_name, time, state)

    def get_persistence_data(self, start_time: datetime | None, end_time: datetime | None) -> OpenhabPersistenceData:
        return self.openhab.get_persistence_data(self.item_name, self.service_name, start_time, end_time)


class TestRRD4j(TestPersistenceBase):

    def __init__(self) -> None:
        super().__init__('rrd4j', 'RRD4jItem')
        self.add_test('RRD4J get', self.test_get)

    def test_get(self) -> None:
        now = datetime.now()
        d = self.get_persistence_data(now - timedelta(seconds=60), now)
        assert d.get_data()


TestRRD4j()


class TestMapDB(TestPersistenceBase):

    def __init__(self) -> None:
        super().__init__('mapdb', 'RRD4jItem')
        self.add_test('MapDB get', self.test_get)

    def test_get(self) -> None:
        now = datetime.now()
        d = self.get_persistence_data(now - timedelta(seconds=60), now)
        assert d.get_data()


TestMapDB()


class TestInMemory(TestPersistenceBase):

    def __init__(self) -> None:
        super().__init__('inmemory', 'InMemoryForecastItem')

        if Connections.get('openhab').context.version >= (4, 1):
            self.add_test('InMemory', self.test_in_memory)
        else:
            print('Skip "TestInMemory" because of no InMemoryDb')

    def test_in_memory(self) -> None:
        now = datetime.now().replace(microsecond=0) + timedelta(seconds=1)
        t1 = now + timedelta(milliseconds=100)
        t2 = now + timedelta(milliseconds=200)
        t3 = now + timedelta(milliseconds=300)

        self.set_persistence_data(t1, 5)
        self.set_persistence_data(t2, 6)
        self.set_persistence_data(t3, 7)

        value = self.get_persistence_data(now - timedelta(milliseconds=1), t3 + timedelta(milliseconds=1))
        objs = value.get_data()

        target = {t1.timestamp(): 5, t2.timestamp(): 6, t3.timestamp(): 7}
        assert objs == target


TestInMemory()
