from HABApp.core.events import ValueUpdateEventFilter

from HABAppTests import TestBaseRule, EventWaiter, OpenhabTmpItem, get_openhab_test_events, \
    get_openhab_test_types, get_openhab_test_states, ItemWaiter


class TestOpenhabEventTypes(TestBaseRule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        # test the states
        for oh_type in get_openhab_test_types():
            self.add_test(f'{oh_type} events', self.test_events, oh_type, get_openhab_test_events(oh_type))

        dimensions = {
            'Length': 'm', 'Temperature': '°C', 'Pressure': 'hPa', 'Speed': 'km/h', 'Intensity': 'W/m²', 'Angle': '°',
            'Dimensionless': '',
        }

        for name, unit in dimensions.items():
            self.add_test(f'Quantity {name} events', self.test_quantity_type_events, name, unit)

    def test_events(self, item_type, test_values):
        item_name = f'{item_type}_value_test'

        with OpenhabTmpItem(item_type, item_name), EventWaiter(item_name, ValueUpdateEventFilter()) as waiter:
            for value in test_values:

                self.openhab.post_update(item_name, value)
                waiter.wait_for_event(value=value)

                # Contact does not support commands
                if item_type != 'Contact':
                    self.openhab.send_command(item_name, value)
                    waiter.wait_for_event(value=value)

    def test_quantity_type_events(self, dimension, unit):
        item_name = f'{dimension}_event_test'
        with OpenhabTmpItem(f'Number:{dimension}', item_name) as item, \
                EventWaiter(item_name, ValueUpdateEventFilter()) as event_waiter, \
                ItemWaiter(item) as item_waiter:

            for state in get_openhab_test_states('Number'):
                self.openhab.post_update(item_name, f'{state} {unit}'.strip())
                event_waiter.wait_for_event(value=state)
                item_waiter.wait_for_state(state)


TestOpenhabEventTypes()
