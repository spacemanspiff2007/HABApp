import logging

from HABAppTests import TestBaseRule

log = logging.getLogger('HABApp.TestParameterFiles')


class TestScheduler(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self):
        super().__init__()

        f = self.run_on_sun('sunrise', self.sunrise_func)
        print(f'Sunrise: {f.get_next_call()}')
        f = self.run_on_sun('sunset', self.sunset_func)
        print(f'Sunset: {f.get_next_call()}')

    def sunrise_func(self):
        print('sunrise!')

    def sunset_func(self):
        print('sunset!')


TestScheduler()
