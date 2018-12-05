import time, datetime, random
import HABApp
#import HABApp.
from HABApp.openhab.events.item_events import ItemStateEvent

class MyRule(HABApp.Rule):

    def __init__(self):
        super().__init__()
        self.listen_event( 'TestSwitchTOGGLE', self.cb, ItemStateEvent)

        self.run_on_day_of_week( datetime.time(14,34,20), ['Mo'], self.cb, 'run_on_day_of_week')

        #self.run_every(5, 1, self.print_ts, 'Sec P1', asdf='P2')

        self.item_list = [ f"CreatedItem{k}" for k in range(200)]

        self.__b_start = 0
        self.__b_val = random.randint(0,9999)


        #self.run_at(datetime.datetime.now(), self.prepare_bench)

    def prepare_bench(self):
        for k in self.item_list:
            self.item_create('string', k)

        self.run_minutely(self.bench_start)
        self.listen_event(self.item_list[-1], self.bench_stop, None)


    def print_ts(self, arg, asdf = None):
        print( f'{time.time():.3f} : {arg}, {asdf}')
        self.post_Update('TestDateTime9', datetime.datetime.now())

    def bench_start(self):
        self.__b_val = str(random.randint(0, 99999999))
        self.__b_start = time.time()
        for k in self.item_list:
            self.post_Update(k, self.__b_val)
        dur = time.time() - self.__b_start
        print(f'bench_start finish: {dur:.3f}')

    def bench_stop(self, event):
        print(f'bench_stop {event}')

        if event.value != self.__b_val:
            return None

        ts_start = time.time()
        while True:
            for k in self.item_list:
                if self.item_state(k) != self.__b_val:
                    break
            else:
                break

            time.sleep(0.2)

        print(f'Wait: {time.time() - ts_start:.3f}')
        dur = time.time() - self.__b_start
        print( f'Dauer: {dur:.3f}')
        print(f'--> {len(self.item_list)/dur:5.3f} changes per sec')


    def cb(self, event):
        print( f'CALLBACK: {event}')
        assert isinstance(event, ItemStateEvent)

        #time.sleep(0.6)

        # s = time.time()
        #
        # for k in range(100):
        #     self.send_Command('TestString9', f"{k}")
        #
        # self.post_Update('TestString8', "11")
        # print( f'dauer: {time.time() - s}')


a = MyRule()




