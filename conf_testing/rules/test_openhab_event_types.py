import datetime
import logging
import time

import HABApp
from HABApp.core.events import ValueUpdateEvent

log = logging.getLogger('HABApp.OpenhabTestEvents')


class TestOpenhabEventTypes(HABApp.Rule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        self.values = {}
        self.values_get = {}

        self.tests = {
            'Color': [ (1, 2, 3)],
            'Contact': ['OPEN', 'CLOSED'],
            'DateTime': [
                datetime.datetime.now(),
                datetime.datetime.now() + datetime.timedelta(10),
                datetime.datetime.now() - datetime.timedelta(10),
            ],
            'Dimmer': [0, 100, 55.5],
            'Location': ["1,2,3", "-1.1,2.2,3.3"],
            'Number': [-111, 222, -13.13, 55.55],
            'Player': ["PLAY", "PAUSE", "REWIND", "FASTFORWARD"],
            'Rollershutter': [0, 100, 30.5],
            'String': ['A', 'B', 'C'],
            'Switch': ['ON', 'OFF'],
        }

        self.run_soon(self.run_tests)

    def run_tests(self):
        for item_type, test_values in self.tests.items():
            item_name = f'{item_type}_value_test'
            self.openhab.create_item(item_type, item_name)

            listener = self.listen_event(item_name, self.value_change, ValueUpdateEvent)
            self.test_values(item_name, test_values, start=True)

            start = time.time()
            while test_values and time.time() <= start + 10:
                time.sleep(0.3)
            duration = time.time() - start
            if duration > start + 10:
                log.error(f'Timeout testing {item_name}')

            HABApp.core.EventBus.remove_listener(listener)
            self.openhab.remove_item( item_name)

    def value_change(self, event):
        assert isinstance(event, ValueUpdateEvent)

        value_get = event.value
        value_set = self.values[event.name]

        equal = False
        if isinstance(value_get, datetime.datetime) and isinstance(value_set, datetime.datetime):
            if value_set.hour == value_get.hour and \
               value_set.minute == value_get.minute and \
               value_set.second == value_get.second and \
               value_set.microsecond // 1000 == value_get.microsecond // 1000 and \
               value_set.year == value_get.year and \
               value_set.month == value_get.month and \
               value_set.day == value_get.day:
                equal = True
        else:
            equal = value_get == value_set

        self.values_get[event.name] = value_get
        (log.debug if equal else log.error)(f'Get  {event.name}: {value_get} [{"x" if equal else " "}]OK')

        assert equal, \
            f'\nset: {value_set} ({type(value_set)})' \
            f'\nis : {value_get} ({type(value_get)})'

    def test_values(self, name, value_list: list, start=False):

        if start:
            pos = 0
        else:
            try:
                pos = value_list.index(self.values[name])
                pos += 1
            except ValueError:
                log.error( f'Value for {name} not found in tests! ({self.values[name]})')
                value_list.clear()
                return None

            if self.values_get.get(name) is None:
                log.error( f'No Value received for {name}')
                value_list.clear()
                return None

        if pos >= len(value_list):
            log.info(f'Test of {name} successful!')
            value_list.clear()
            return None

        next_val = value_list[pos]
        self.values[name] = next_val
        self.openhab.post_update(name, next_val)
        log.debug(f'Post {name}: {next_val}')

        self.run_soon(self.test_values, name, value_list)



TestOpenhabEventTypes()
