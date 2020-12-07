import asyncio
import datetime
import random
import statistics
import time

import HABApp
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.openhab.items import NumberItem

WAIT_PREPARE = 5
RUN_EVERY = 5


class OpenhabBenchRule(HABApp.Rule):

    def __init__(self):
        super().__init__()

        self.item_list = [f"BenchItem{k}" for k in range(300)]

        self.__b_start = 0
        self.__b_val = random.randint(0, 9999)

        self.run_in(WAIT_PREPARE, self.prepare_bench)

        self.pings = []
        self.ping_item = NumberItem.get_item('Ping')
        self.ping_item.listen_event(self.ping_received, ValueUpdateEvent)

    def prepare_bench(self):
        print('')
        print('Benchmark item creation')

        start = time.time()
        for k in self.item_list:
            self.openhab.create_item('String', k)

        self.run_every(None, datetime.timedelta(minutes=RUN_EVERY), self.bench_start)
        self.listen_event(self.item_list[-1], self.bench_stop, ValueChangeEvent)

        dur = time.time() - start
        print(f'Updated {len(self.item_list)} item definitions in {dur:.3f}s'
              f' --> {len(self.item_list)/dur:5.3f} updates per sec')

    def ping_received(self, event: ValueUpdateEvent):
        self.pings.append(event.value)

    def bench_start(self):
        print('')
        print('Benchmark value update creation')
        self.__b_val = str(random.randint(0, 99999999))
        self.__b_start = time.time()
        for k in self.item_list:
            self.openhab.post_update(k, self.__b_val)

    async def bench_stop(self, event):
        if event.value != self.__b_val:
            return None

        ts_start = time.time()
        while True:
            for k in self.item_list:
                if HABApp.openhab.items.OpenhabItem.get_item(k).value != self.__b_val:
                    break
            else:
                break

            await asyncio.sleep(0.1)

        print(f'Wait: {time.time() - ts_start:.3f}')
        dur = time.time() - self.__b_start
        print(f'Benchmark duration: {dur:.3f}s --> {len(self.item_list)/dur:5.3f} updates per sec')
        print(f'Pings ({len(self.pings)}): min: {min(self.pings):.1f} max: {max(self.pings):.1f} '
              f'median: {statistics.median(self.pings):.1f}')
        self.pings.clear()


OpenhabBenchRule()
