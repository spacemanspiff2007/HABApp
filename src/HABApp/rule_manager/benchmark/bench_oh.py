import random
import time
from collections import deque
from threading import Lock

import HABApp
from HABApp.core.events import ValueUpdateEvent, ValueUpdateEventFilter
from HABApp.openhab.items import NumberItem

from .bench_base import BenchBaseRule
from .bench_times import BenchContainer, BenchTime


LOCK = Lock()


class OpenhabBenchRule(BenchBaseRule):
    BENCH_TYPE = 'openHAB'

    RTT_BENCH_MAX = 15

    def __init__(self) -> None:
        super().__init__()

        self.name_list = [f'BenchItem{k}' for k in range(300)]

        self.time_sent = 0.0
        self.bench_started = 0.0
        self.bench_times_container = BenchContainer()
        self.bench_times: BenchTime = None

        self.item_values = deque()
        self.item_name = ''
        self.item_obj: NumberItem | None = None

        self.load_listener = []

    def cleanup(self):
        self.stop_load()

        all_items = set(HABApp.core.Items.get_item_names())
        to_rem = set(self.name_list) & all_items

        if not to_rem:
            return None

        print('Cleanup ... ', end='')
        for name in to_rem:
            self.oh.remove_item(name)
        print('complete')

    def set_up(self) -> None:
        self.cleanup()
        self.item_name = self.name_list[0]

    def tear_down(self) -> None:
        self.cleanup()

    def run_bench(self) -> None:
        # These are the benchmarks
        self.bench_item_create()
        self.bench_rtt_time()

    def bench_item_create(self) -> None:
        print('Bench item operations ', end='')

        max_duration = 10   # how long should each bench take

        times = BenchContainer()

        start_bench = time.time()
        b = times.create('create item')
        for k in self.name_list:
            start = time.time()
            self.openhab.create_item('Number', k, label='MyLabel')
            b.times.append(time.time() - start)

            # limit bench time on weak devices
            if time.time() - start_bench > max_duration:
                break

        time.sleep(0.2)

        print('.', end='')
        start_bench = time.time()
        b = times.create('update item')
        for k in self.name_list:
            start = time.time()
            self.openhab.create_item('Number', k, label='New Label')
            b.times.append(time.time() - start)

            # limit bench time on weak devices
            if time.time() - start_bench > max_duration:
                break

        time.sleep(0.2)

        print('.', end='')
        start_bench = time.time()
        b = times.create('delete item')
        for k in self.name_list:
            start = time.time()
            self.openhab.remove_item(k)
            b.times.append(time.time() - start)

            # limit bench time on weak devices
            if time.time() - start_bench > max_duration:
                break

        print('. done!\n')
        times.show()

    def bench_rtt_time(self) -> None:
        self.openhab.create_item('Number', self.item_name, label='MyLabel')
        time.sleep(2)

        print('Bench item state update ', end='')
        self.bench_times_container = BenchContainer()

        self.run_rtt('rtt idle')
        time.sleep(2)
        self.run_rtt('async rtt idle', do_async=True)
        time.sleep(2)
        self.item_obj = NumberItem.get_item(self.item_name)
        self.run_rtt('rtt idle item')
        time.sleep(2)
        self.run_rtt('async rtt idle item', do_async=True)
        time.sleep(2)

        self.item_obj = None

        self.start_load()
        self.run_rtt('rtt load (+10x)')
        time.sleep(2)
        self.run_rtt('async rtt load (+10x)', do_async=True)
        self.stop_load()

        self.item_obj = NumberItem.get_item(self.item_name)

        self.start_load()
        self.run_rtt('rtt load item (+10x)')
        time.sleep(2)
        self.run_rtt('async rtt load item (+10x)', do_async=True)
        self.stop_load()

        print(' done!\n')
        self.bench_times_container.show()

    def start_load(self) -> None:

        for i in range(10, 20):
            self.openhab.create_item('Number', self.name_list[i], label='MyLabel')

        time.sleep(1)

        for i in range(10, 20):
            if self.item_obj is None:
                def load_cb(event, item: str = self.name_list[i]) -> None:
                    self.openhab.post_update(item, random.randint(0, 99999999), transport='http')
            else:
                def load_cb(event, item: NumberItem = NumberItem.get_item(self.name_list[i])) -> None:  # noqa: B008
                    item.oh_post_update(random.randint(0, 99999999))

            listener = self.listen_event(self.name_list[i], load_cb, ValueUpdateEventFilter())
            self.load_listener.append(listener)

        # start
        for i in range(10, 20):
            self.openhab.post_update(self.name_list[i], random.randint(0, 99999999))

    def stop_load(self) -> None:
        for list in self.load_listener:
            list.cancel()
        self.load_listener.clear()
        time.sleep(3)

    def run_rtt(self, test_name: str, do_async=False) -> None:
        for _ in range(5_000):
            self.item_values.append(random.randint(0, 99_999_999))

        listener = self.listen_event(
            self.item_name, self.proceed_item_val if not do_async else self.a_proceed_item_val, ValueUpdateEventFilter()
        )

        self.bench_times = self.bench_times_container.create(test_name)

        self.bench_started = time.time()
        self.time_sent = time.time()
        self.openhab.post_update(self.item_name, self.item_values[0])

        self.run.soon(LOCK.acquire)
        time.sleep(1)
        LOCK.acquire(True, OpenhabBenchRule.RTT_BENCH_MAX)

        listener.cancel()
        if LOCK.locked():
            LOCK.release()

        print('.', end='')

    def proceed_item_val(self, event: ValueUpdateEvent):
        if event.value != self.item_values[0]:
            return None

        self.bench_times.times.append(time.time() - self.time_sent)

        # Time up -> stop benchmark
        if time.time() - self.bench_started > OpenhabBenchRule.RTT_BENCH_MAX:
            LOCK.release()
            return None

        # No items left -> stop benchmark
        try:
            self.item_values.popleft()
            next_value = self.item_values[0]
        except IndexError:
            LOCK.release()
            return None

        self.time_sent = time.time()

        if self.item_obj is not None:
            self.item_obj.oh_post_update(next_value)
        else:
            self.openhab.post_update(self.item_name, next_value, transport='http')

    async def a_proceed_item_val(self, event: ValueUpdateEvent) -> None:
        self.proceed_item_val(event)
