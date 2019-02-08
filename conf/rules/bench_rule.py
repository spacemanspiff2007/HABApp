import datetime
import random
import time

import HABApp
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.openhab.events import ItemStateEvent

class OpenhabBenchRule(HABApp.Rule):

    def __init__(self):
        super().__init__()

        self.item_list = [ f"CreatedItem{k}" for k in range(200)]

        self.__b_start = 0
        self.__b_val = random.randint(0,9999)

        self.run_soon(self.prepare_bench)

    def prepare_bench(self):
        for k in self.item_list:
            self.create_openhab_item('string', k)

        self.run_minutely(self.bench_start)
        self.listen_event(self.item_list[-1], self.bench_stop, ValueChangeEvent)

    def bench_start(self):
        self.__b_val = str(random.randint(0, 99999999))
        self.__b_start = time.time()
        for k in self.item_list:
            self.post_update(k, self.__b_val)
        dur = time.time() - self.__b_start
        print(f'bench_start finish: {dur:.3f}')

    def bench_stop(self, event):
        print(f'bench_stop {event}')

        if event.value != self.__b_val:
            return None

        ts_start = time.time()
        while True:
            for k in self.item_list:
                if self.get_item_state(k) != self.__b_val:
                    break
            else:
                break

            time.sleep(0.2)

        print(f'Wait: {time.time() - ts_start:.3f}')
        dur = time.time() - self.__b_start
        print( f'Dauer: {dur:.3f}')
        print(f'--> {len(self.item_list)/dur:5.3f} changes per sec')


OpenhabBenchRule()