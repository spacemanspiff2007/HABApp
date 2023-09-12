import random
import time
from collections import deque
from threading import Lock

import HABApp
from HABApp.core.events import ValueUpdateEvent, ValueUpdateEventFilter
from .bench_base import BenchBaseRule
from .bench_times import BenchContainer, BenchTime
from HABApp.mqtt.interface_sync import publish

LOCK = Lock()


class MqttBenchRule(BenchBaseRule):
    BENCH_TYPE = 'MQTT'

    def __init__(self):
        super().__init__()

        self.name_list = [f'test/BenchItem{k}' for k in range(300)]

        self.time_sent = 0.0
        self.bench_started = 0.0
        self.bench_times_container = BenchContainer()
        self.bench_times: BenchTime = None

        self.name = ''
        self.values = deque()

    def cleanup(self):
        for n in self.name_list:
            if HABApp.core.Items.item_exists(n):
                HABApp.core.Items.pop_item(n)

    def set_up(self):
        self.cleanup()

    def tear_down(self):
        pass
        self.cleanup()

    def run_bench(self):
        # These are the benchmarks
        self.bench_rtt_time()

    def bench_rtt_time(self):
        print('Bench events ', end='')
        self.bench_times_container = BenchContainer()

        self.run_rtt('rtt idle')
        self.run_rtt('async rtt idle', do_async=True)

        # self.start_load()
        # self.run_rtt('rtt load (+10x)')
        # self.run_rtt('async rtt load (+10x)', do_async=True)
        # self.stop_load()

        print(' done!\n')
        time.sleep(0.1)
        self.bench_times_container.show()

    def run_rtt(self, test_name, do_async=False):
        self.name = self.name_list[0]
        HABApp.mqtt.items.MqttItem.get_create_item(self.name)

        for i in range(50_000):
            self.values.append(random.randint(0, 99999999))

        listener = self.listen_event(
            self.name,
            self.post_next_event_val if not do_async else self.a_post_next_event_val,
            ValueUpdateEventFilter()
        )

        self.bench_times = self.bench_times_container.create(test_name)

        self.time_sent = time.time()
        publish(self.name, self.values[0])

        self.run.soon(LOCK.acquire)
        time.sleep(1)
        LOCK.acquire(True, 5)

        listener.cancel()
        if LOCK.locked():
            LOCK.release()

        print('.', end='')

    def post_next_event_val(self, event):
        if event.value != self.values[0]:
            return None

        self.bench_times.times.append(time.time() - self.time_sent)

        # No items left -> stop benchmark
        try:
            self.values.popleft()
        except IndexError:
            LOCK.release()
            return None

        if not self.values:
            LOCK.release()
            return None

        self.time_sent = time.time()
        publish(self.name, self.values[0])

    async def a_post_next_event_val(self, event: ValueUpdateEvent):
        self.post_next_event_val(event)
