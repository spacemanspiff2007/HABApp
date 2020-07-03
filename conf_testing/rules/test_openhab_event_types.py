from HABApp.core.events import ValueUpdateEvent
from HABApp.openhab.definitions.definitions import ITEM_DIMENSION

from HABAppTests import TestBaseRule, EventWaiter, OpenhabTmpItem, get_openhab_test_events, \
    get_openhab_test_types, get_openhab_test_states, ItemWaiter


class TestOpenhabEventTypes(TestBaseRule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        # test the states
        for oh_type in get_openhab_test_types():
            self.add_test( f'{oh_type} events', self.test_events, oh_type, get_openhab_test_events(oh_type))

        for dimension in ITEM_DIMENSION:
            self.add_test(f'Quantity {dimension} events', self.test_quantity_type_events, dimension)

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

    def test_quantity_type_events(self, dimension):

        unit_of_dimension = {
            'Length': 'm', 'Temperature': '°C', 'Pressure': 'hPa', 'Speed': 'km/h', 'Intensity': 'W/m²', 'Angle': '°'
        }

        item_name = f'{dimension}_event_test'
        with OpenhabTmpItem(item_name, f'Number:{dimension}') as item, \
                EventWaiter(item_name, ValueUpdateEvent) as event_watier, \
                ItemWaiter(item) as item_waiter:

            for state in get_openhab_test_states('Number'):
                self.openhab.post_update(item_name, f'{state} {unit_of_dimension[dimension]}')
                event_watier.wait_for_event(state)
                item_waiter.wait_for_state(state)

            all_events_ok = event_watier.events_ok
        return all_events_ok


TestOpenhabEventTypes()
