from datetime import datetime, time, timedelta

from HABApp import Rule


class MyRule(Rule):

    def __init__(self) -> None:
        super().__init__()

        self.run.on_day_of_week(time=time(14, 34, 20), weekdays=['Mo'], callback=self.run_mondays)

        self.run.every(timedelta(seconds=5), 3, self.run_every_3s, 'arg 1', asdf='kwarg 1')

        self.run.on_workdays(time(15, 00), self.run_workdays)
        self.run.on_weekends(time(15, 00), self.run_weekends)

    def run_every_3s(self, arg, asdf = None) -> None:
        print(f'run_ever_3s: {datetime.now().replace(microsecond=0)} : {arg}, {asdf}')

    def run_mondays(self) -> None:
        print('Today is monday!')

    def run_workdays(self) -> None:
        print('Today is a workday!')

    def run_weekends(self) -> None:
        print('Finally weekend!')


MyRule()
