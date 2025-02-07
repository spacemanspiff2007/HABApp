from HABAppTests import (
    EventWaiter,
    ItemWaiter,
    OpenhabTmpItem,
    TestBaseRule,
    get_openhab_item_names,
    get_openhab_test_commands,
    get_openhab_test_states,
)

from HABApp.core.events import ValueUpdateEventFilter
from HABApp.openhab.events import ItemCommandEventFilter


class TestOpenhabEventTypes(TestBaseRule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self) -> None:
        super().__init__()

        for oh_type in get_openhab_item_names():
            self.add_test(
                f'{oh_type} updates', self.test_item, oh_type,
                get_openhab_test_states(oh_type), get_openhab_test_commands(oh_type)
            )

        dimensions = {
            'Length': 'm', 'Temperature': '°C', 'Pressure': 'hPa', 'Speed': 'km/h', 'Intensity': 'W/m²', 'Angle': '°',
            'Dimensionless': '',
        }
        for name, unit in dimensions.items():
            self.add_test(f'Quantity {name} events', self.test_quantity_type_events, name, unit)

    def test_item(self, item_type: str, test_states: tuple, test_commands: tuple) -> None:
        item_name = f'{item_type}_value_test'

        with (OpenhabTmpItem(item_type, item_name) as item,
              EventWaiter(item_name, ValueUpdateEventFilter()) as state_waiter,
              EventWaiter(item_name, ItemCommandEventFilter()) as command_waiter):

            for post_value, receive_value in test_states:
                item.oh_post_update(post_value)
                state_waiter.wait_for_event(value=receive_value)

            for send_command, receive_value in test_commands:
                item.oh_send_command(send_command)
                command_waiter.wait_for_event(value=receive_value)

            for send_command, receive_value in test_commands:
                item.command_value(send_command)
                command_waiter.wait_for_event(value=receive_value)

    def test_quantity_type_events(self, dimension, unit) -> None:
        item_name = f'{dimension}_event_test'
        with OpenhabTmpItem(f'Number:{dimension}', item_name) as item, \
                EventWaiter(item_name, ValueUpdateEventFilter()) as event_waiter, \
                ItemWaiter(item) as item_waiter:

            for state_send, state_receive in get_openhab_test_states('Number'):
                if state_receive is None:
                    continue
                self.openhab.post_update(item_name, f'{state_send} {unit}'.strip())
                event_waiter.wait_for_event(value=state_receive)
                item_waiter.wait_for_state(state_receive)


TestOpenhabEventTypes()
