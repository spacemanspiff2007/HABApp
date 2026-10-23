import inspect
from typing import get_type_hints

import pytest
from tests.helpers.inspect import check_class_annotations, get_module_classes

from HABApp.openhab.events import (
    EventSourceFilter,
    ItemAddedEvent,
    ItemCommandEvent,
    ItemCommandEventFilter,
    ItemStateChangedEvent,
    ItemStateChangedEventFilter,
    ItemStateUpdatedEvent,
    ItemStateUpdatedEventFilter,
    OpenhabEvent,
)
from HABApp.openhab.types import EventSourceStr


def test_class_annotations() -> None:
    """EventFilter relies on the class annotations, so we test that every event has those"""

    exclude = (
        'OpenhabEvent',
        'ItemStateChangedEventFilter', 'ItemStateUpdatedEventFilter', 'ItemStateEventFilter',
        'ItemCommandEventFilter', 'EventSourceFilter')
    for cls in get_module_classes('HABApp.openhab.events', exclude).values():
        check_class_annotations(
            cls,
            init_alias={'initial_value': 'value', 'group_names': 'groups', 'thing_type': 'type'},
        )


def test_oh_filters() -> None:

    f = ItemStateUpdatedEventFilter(value=1)
    assert f.event_class is ItemStateUpdatedEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1

    f = ItemCommandEventFilter(value=1)
    assert f.event_class is ItemCommandEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1

    f = ItemStateChangedEventFilter(old_value='asdf')
    assert f.event_class is ItemStateChangedEvent
    assert f.attr_name1 == 'old_value'
    assert f.attr_value1 == 'asdf'

    f = ItemStateChangedEventFilter(old_value='asdf', value=1)
    assert f.event_class is ItemStateChangedEvent
    assert f.attr_name1 == 'value'
    assert f.attr_value1 == 1
    assert f.attr_name2 == 'old_value'
    assert f.attr_value2 == 'asdf'


def _event(source: str | None) -> ItemStateChangedEvent:
    return ItemStateChangedEvent(
        'item', 1, 0, last_state_update=None, last_state_change=None,
        source=EventSourceStr(source) if source is not None else None,
    )


class TestEventSourceFilter:

    @staticmethod
    def _events_with_source() -> list[type[OpenhabEvent]]:
        classes = get_module_classes('HABApp.openhab.events', subclass=OpenhabEvent).values()
        return [cls for cls in classes if 'source' in get_type_hints(cls)]

    def test_requires_argument(self) -> None:
        with pytest.raises(ValueError, match='At least one'):
            EventSourceFilter()

    def test_no_source(self) -> None:
        f = EventSourceFilter(bundle='HABApp')
        assert f.trigger(_event(None)) is False
        assert f.trigger(_event('')) is False

        # event class that doesn't have a source attribute at all
        other = ItemAddedEvent('item', 'Switch', None, frozenset(), frozenset())
        assert f.trigger(other) is False

        # arbitrary object without a source attribute
        class NoSource:
            pass

        assert f.trigger(NoSource()) is False

    def test_describe(self) -> None:
        assert EventSourceFilter(bundle='HABApp').describe() == 'EventSourceFilter(bundle=HABApp)'
        assert EventSourceFilter(actor='my_rule').describe() == 'EventSourceFilter(actor=my_rule)'
        assert EventSourceFilter(bundle='HABApp', actor='my_rule').describe() == \
            'EventSourceFilter(bundle=HABApp, actor=my_rule)'

    @pytest.mark.parametrize('cls', _events_with_source(), ids=lambda cls: cls.__name__)
    def test_all_events_with_source(self, cls: type[OpenhabEvent]) -> None:
        # happy path: only "source" is filled with a meaningful value, the rest is None
        source = EventSourceStr('HABApp.my_rule')
        kwargs = {name: source if name == 'source' else None for name in inspect.signature(cls).parameters}
        event = cls(**kwargs)

        assert EventSourceFilter(bundle='HABApp').trigger(event) is True
        assert EventSourceFilter(actor='my_rule').trigger(event) is True
        assert EventSourceFilter(bundle='HABApp', actor='my_rule').trigger(event) is True
        assert EventSourceFilter(bundle='other').trigger(event) is False
        assert EventSourceFilter(actor='other').trigger(event) is False

        # both criteria must match (and), not just one of them (or)
        assert EventSourceFilter(bundle='HABApp', actor='other').trigger(event) is False
        assert EventSourceFilter(bundle='other', actor='my_rule').trigger(event) is False
