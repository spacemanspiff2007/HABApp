import datetime
import typing

import HABApp.core
import HABApp.openhab.events

StateTypes = typing.Union[str, int, float, datetime.datetime]


def add_mock_item(
    item_type: typing.Type[HABApp.openhab.items.OpenhabItem],
    name: str,
    initial_value: typing.Optional[StateTypes] = None,
) -> HABApp.openhab.items.OpenhabItem:
    """Add a mock item.
    :param item_type: Type of the mock item
    :param name: Name of the mock item
    :param initial_value: initial value
    """
    if HABApp.core.Items.item_exists(name):
        HABApp.core.Items.pop_item(name)
    item = item_type(name, initial_value)
    HABApp.core.Items.add_item(item)
    return item


def set_state(item_name: str, value: StateTypes) -> None:
    """Helper to set state of item.
    :param item_name: name of item
    :param value: state which should be set
    """
    item = HABApp.openhab.items.OpenhabItem.get_item(item_name)
    if isinstance(item, HABApp.openhab.items.DimmerItem) and value in {"ON", "OFF"}:
        if value == "ON":
            value = 100
        else:
            value = 0

    try:
        item.set_value(value)
    except AssertionError:
        print(f"Could not set '{value}' to '{item_name}'")


def send_command(
    item_name: str, new_value: StateTypes, old_value: typing.Optional[StateTypes] = None
) -> None:
    """Replacement of send_command for unit-tests.
    :param item_name: Name of item
    :param new_value: new value
    :param old_value: previous value
    """
    set_state(item_name, new_value)
    if old_value and old_value != new_value:
        HABApp.core.EventBus.post_event(
            item_name,
            HABApp.openhab.events.ItemStateChangedEvent(
                item_name, new_value, old_value
            ),
        )
    HABApp.core.EventBus.post_event(
        item_name, HABApp.openhab.events.ItemStateEvent(item_name, new_value)
    )


def item_state_change_event(
    item_name: str, value: StateTypes, old_value: typing.Optional[StateTypes] = None
) -> None:
    """Post a state change event to the event bus
    :param item_name: name of item
    :param value: value of the event
    :param old_value: previous value
    """
    prev_value = (
        old_value
        if old_value
        else HABApp.openhab.items.OpenhabItem.get_item(item_name).value
    )
    set_state(item_name, value)
    HABApp.core.EventBus.post_event(
        item_name,
        HABApp.openhab.events.ItemStateChangedEvent(item_name, value, prev_value),
    )
