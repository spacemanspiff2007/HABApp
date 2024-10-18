import time
from unittest.mock import MagicMock

from whenever import Instant, patch_current_time

from HABApp.core.events import NoEventFilter, ValueCommandEvent
from HABApp.core.internals import ItemRegistry
from HABApp.core.items import Item
from tests.helpers import TestEventBus


class ItemTests:
    ITEM_CLASS: type[Item] | None = None
    ITEM_VALUES: tuple | None = None

    def get_item(self) -> Item:
        return self.ITEM_CLASS('test_name')

    def get_create_item(self) -> Item:
        return self.ITEM_CLASS.get_create_item(name='test_name')

    def test_item_params(self) -> None:
        assert self.ITEM_CLASS is not None
        assert self.ITEM_VALUES is not None

    def test_repr(self) -> None:
        item = self.get_item()
        assert repr(item)
        assert str(item)

    def test_factories(self, ir: ItemRegistry) -> None:
        assert not ir.item_exists(self.get_item())

        obj = self.get_create_item()
        assert isinstance(obj, self.ITEM_CLASS)

        obj2 = self.ITEM_CLASS.get_item(name=obj.name)
        assert obj is obj2

    def test_var_names(self) -> None:
        values = self.ITEM_VALUES
        item = self.get_item()
        # assert item.value is None, f'{item.value} ({type(item.value)})'

        item.set_value(values[0])
        assert item.value == values[0]

        item.post_value(values[0])
        item.get_value(default_value='asdf')

    def test_time_value_update(self) -> None:
        instant = Instant.from_utc(2001, 1, 1, hour=1)

        for value in self.ITEM_VALUES:
            with patch_current_time(instant.subtract(seconds=5), keep_ticking=False) as p:
                item = self.get_item()
                item.set_value(value)

                p.shift(seconds=5)
                item.set_value(value)

                assert item._last_update.instant == instant
                assert item._last_change.instant == instant.subtract(seconds=5)

    def test_time_value_change(self) -> None:
        item = self.get_item()
        instant = Instant.from_utc(2001, 1, 1, hour=1)

        for value in self.ITEM_VALUES:
            instant.add(hours=1)
            with patch_current_time(instant, keep_ticking=False):
                item.set_value(value)
                assert item._last_update.instant == instant
                assert item._last_change.instant == instant

    def test_time_funcs(self) -> None:
        item = self.get_item()

        now1 = Instant.now()
        time.sleep(0.000_001)

        item.set_value(self.ITEM_VALUES[0])

        time.sleep(0.000_001)
        now2 = Instant.now()
        time.sleep(0.000_001)

        assert now1 < item.last_change < now2, f'\n{now1}\n{item.last_change}\n{now2}'
        assert now1 < item.last_update < now2, f'\n{now1}\n{item.last_update}\n{now2}'

        item.set_value(self.ITEM_VALUES[0])

        time.sleep(0.000_001)
        now3 = Instant.now()

        assert now1 < item.last_change < now2
        assert now2 < item.last_update < now3

    def test_post_if(self) -> None:
        i = self.get_item()
        assert i.post_value_if(0, is_=None)
        assert i.post_value_if(1, eq=0)
        assert not i.post_value_if(1, eq=0)

    def test_post_command(self, sync_worker, eb: TestEventBus) -> None:
        i = self.get_item()

        mock = MagicMock()
        eb.listen_events(i.name, mock, NoEventFilter())
        mock.assert_not_called()

        value = self.ITEM_VALUES[0]
        i.command_value(value)
        mock.assert_called()

        update = mock.call_args_list[0][0][0]
        assert isinstance(update, ValueCommandEvent)
        assert update.name == i.name
        assert update.value == value
