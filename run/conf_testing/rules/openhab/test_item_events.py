from typing import Final

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
from HABApp.openhab.events import (
    ItemCommandEvent,
    ItemCommandEventFilter,
    ItemStateChangedEvent,
    ItemStateUpdatedEvent,
    ItemStateUpdatedEventFilter,
)
from HABApp.openhab.items import NumberItem


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

        self.add_test('EventSourceCommandHttp', self.test_event_source_command, 'http')
        self.add_test('EventSourceCommandWs', self.test_event_source_command, 'websocket')
        self.add_test('EventSourceUpdateHttp', self.test_event_source_update, 'http')
        self.add_test('EventSourceUpdateWs', self.test_event_source_update, 'websocket')

    def test_item(self, item_type: str, test_states: tuple, test_commands: tuple) -> None:
        item_name = f'{item_type}_value_test'

        with (OpenhabTmpItem(item_type, item_name) as item,
              EventWaiter(item_name, ValueUpdateEventFilter()) as state_waiter,
              EventWaiter(item_name, ItemCommandEventFilter()) as command_waiter):

            # check that the event is properly received
            for post_value, receive_value in test_states:
                item.oh_post_update(post_value)
                state_waiter.wait_for_event(value=receive_value)

            # use oh_send_command to send commands
            for send_command, receive_value in test_commands:
                item.oh_send_command(send_command)
                command_waiter.wait_for_event(value=receive_value)

            # use command_value to send commands
            for send_command, receive_value in test_commands:
                item.command_value(send_command)
                command_waiter.wait_for_event(value=receive_value)

    def test_quantity_type_events(self, dimension, unit) -> None:
        item_name = f'{dimension}_event_test'
        with OpenhabTmpItem(f'Number:{dimension}', item_name) as item, \
                EventWaiter(item_name, ValueUpdateEventFilter()) as event_waiter, \
                ItemWaiter(item) as item_waiter:

            for post_func in (item.oh_post_update, lambda x: self.openhab.post_update(item_name, x)):

                for post_value, receive_value in get_openhab_test_states('Number'):
                    if unit and post_value is not None:
                        post_value = f'{post_value} {unit}'  # noqa: PLW2901

                    post_func(post_value)
                    event_waiter.wait_for_event(value=receive_value)
                    item_waiter.wait_for_state(receive_value)

    def test_event_source_command(self, transport: str) -> None:
        with OpenhabTmpItem('Number') as item, EventWaiter(item.name, ItemCommandEventFilter()) as event_waiter:
            # test manual source
            self.oh.send_command(item.name, 5, source='TestSource', transport=transport)
            event: ItemCommandEvent = event_waiter.wait_for_event()
            assert event.source == 'HABApp.TestSource'

            # automatic source
            self.oh.send_command(item.name, 6, source='TestSource', transport=transport)
            event: ItemCommandEvent = event_waiter.wait_for_event()
            assert event.source == 'HABApp.TestOpenhabEventTypes'

    def test_event_source_update(self, transport: str) -> None:

        events: list[ItemStateUpdatedEvent | ItemStateChangedEvent] = []

        def _on_event(event: ItemStateUpdatedEvent | ItemStateChangedEvent) -> None:
            assert isinstance(event, (ItemStateUpdatedEvent, ItemStateChangedEvent))
            events.append(event)

        with OpenhabTmpItem('Number') as item, EventWaiter(item.name, ItemStateUpdatedEventFilter()) as event_waiter:

            NumberItem.get_item(item.name).listen_event(_on_event)

            # test manual source
            value_1: Final = 5
            self.oh.post_update(item.name, value_1, source='TestSource_1', transport=transport)
            self.oh.post_update(item.name, value_1, source='TestSource_2', transport=transport)

            # automatic source
            value_2: Final = 6
            self.oh.post_update(item.name, value_2, transport=transport)
            self.oh.post_update(item.name, value_2, transport=transport)
            event_waiter.wait_for_event()

        e1, e2, e3, e4, e5, e6 = events

        assert isinstance(e1, ItemStateUpdatedEvent)
        assert e1.source is None
        assert e1.value == value_1

        assert isinstance(e2, ItemStateChangedEvent)
        assert e2.source == 'HABApp.TestSource_1'
        assert e2.value == value_1

        assert isinstance(e3, ItemStateUpdatedEvent)
        assert e3.source is None
        assert e3.value == value_1

        assert isinstance(e4, ItemStateUpdatedEvent)
        assert e4.source is None
        assert e4.value == value_2

        assert isinstance(e5, ItemStateChangedEvent)
        assert e5.source == 'HABApp.TestOpenhabEventTypes'
        assert e5.value == value_2

        assert isinstance(e6, ItemStateUpdatedEvent)
        assert e6.source is None
        assert e6.value == value_2


TestOpenhabEventTypes()
