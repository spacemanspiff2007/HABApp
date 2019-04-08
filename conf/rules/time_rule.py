import datetime
import time

import HABApp


class MyRule(HABApp.Rule):

    def __init__(self):
        super().__init__()

        self.run_on_day_of_week(
            datetime.time(14, 34, 20),
            weekdays=['Mo'],
            callback=self.run_mondays
        )

        self.run_every(datetime.timedelta(seconds=5), 3, self.run_every_3s, 'arg 1', asdf='kwarg 1')

        self.run_on_workdays(datetime.time( 15, 00), self.run_workdays)
        self.run_on_weekends(datetime.time( 15, 00), self.run_weekends)

    def run_every_3s(self, arg, asdf = None):
        print( f'run_ever_3s: {time.time():.3f} : {arg}, {asdf}')

    def run_mondays(self):
        print('Today is monday!')

    def run_workdays(self):
        print('Today is a workday!')

    def run_weekends(self):
        print('Today is weekend!')


a = MyRule()







