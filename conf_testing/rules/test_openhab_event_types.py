import datetime
import logging
import time

import HABApp
from HABApp.core.events import ValueUpdateEvent

log = logging.getLogger('HABApp.OpenhabTestEvents')

from HABAppTests import TestBaseRule, EventWaiter, OpenhabTmpItem, get_openhab_test_events, get_openhab_test_types

class TestOpenhabEventTypes(TestBaseRule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        # test the states
        for oh_type in get_openhab_test_types():
            self.add_test( f'{oh_type} events', self.test_events, oh_type, get_openhab_test_events(oh_type))


    def test_events(self, item_type, test_values):
        item_name = f'{item_type}_value_test'

        with OpenhabTmpItem(item_name, item_type), EventWaiter(item_name, ValueUpdateEvent) as waiter:
            for value in test_values:

                self.openhab.post_update(item_name, value)
                waiter.wait_for_event(value)

                # Contact does not support commands
                if item_type != 'Contact':
                    self.openhab.send_command(item_name, value)
                    waiter.wait_for_event(value)

            all_events_ok = waiter.events_ok
        return all_events_ok


TestOpenhabEventTypes()
