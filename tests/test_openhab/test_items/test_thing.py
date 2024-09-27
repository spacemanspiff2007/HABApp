from typing import Any
from unittest.mock import Mock

import pytest
from immutables import Map
from whenever import Instant, patch_current_time

import HABApp
from HABApp.core.internals import ItemRegistry
from HABApp.openhab import process_events as process_events_module
from HABApp.openhab.events import ThingAddedEvent, ThingStatusInfoEvent, ThingUpdatedEvent
from HABApp.openhab.items import Thing
from HABApp.openhab.map_events import get_event


@pytest.fixture(scope='function')
def test_thing(ir: ItemRegistry):
    with patch_current_time(Instant.from_utc(2000, 1, 1), keep_ticking=False):
        thing = HABApp.openhab.items.Thing('test_thing')
        yield thing

def get_status_event(status: str) -> ThingStatusInfoEvent:
    data = {
        'topic': 'openhab/things/test_thing/status',
        'payload': f'{{"status":"{status}","statusDetail":"NONE"}}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    return event


def test_thing_status_events(test_thing: Thing) -> None:

    assert test_thing.status == 'UNINITIALIZED'

    # initial set -> update and change
    instant1 = Instant.from_utc(2000, 1, 1, 1)
    with patch_current_time(instant1, keep_ticking=False):
        test_thing.process_event(get_status_event('ONLINE'))
        assert test_thing.status == 'ONLINE'
        assert test_thing._last_update.instant == instant1
        assert test_thing._last_change.instant == instant1

    # second set -> update
    instant2 = Instant.from_utc(2000, 1, 1, 2)
    with patch_current_time(instant2, keep_ticking=False):
        test_thing.process_event(get_status_event('ONLINE'))
        assert test_thing.status == 'ONLINE'
        assert test_thing._last_update.instant == instant2
        assert test_thing._last_change.instant == instant1

    # third set -> update & change
    instant3 = Instant.from_utc(2000, 1, 1, 3)
    with patch_current_time(instant3, keep_ticking=False):
        test_thing.process_event(get_status_event('INITIALIZING'))
        assert test_thing.status == 'INITIALIZING'
        assert test_thing._last_update.instant == instant3
        assert test_thing._last_change.instant == instant3


def test_thing_updated_event(test_thing: Thing) -> None:

    class MyThingUpdatedEvent(ThingUpdatedEvent):
        def __init__(self, name: str = '', thing_type: str = '', label: str = '', location='',
                     channels: list[dict[str, Any]] = [],
                     configuration: dict[str, Any] = {}, properties: dict[str, str] = {}) -> None:
            super().__init__(name, thing_type, label, location, channels, configuration, properties)

    assert test_thing.properties == Map()
    assert test_thing.configuration == Map()

    # initial set of configuration -> update and change
    instant1 = Instant.from_utc(2000, 1, 1, 1)
    with patch_current_time(instant1, keep_ticking=False):
        test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}))
        assert test_thing.label == ''
        assert test_thing.location == ''
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map()
        assert test_thing._last_update.instant == instant1
        assert test_thing._last_change.instant == instant1

    # second set of configuration -> update
    instant2 = Instant.from_utc(2000, 1, 1, 2)
    with patch_current_time(instant2, keep_ticking=False):
        test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}))
        assert test_thing.label == ''
        assert test_thing.location == ''
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map()
        assert test_thing._last_update.instant == instant2
        assert test_thing._last_change.instant == instant1

    # initial set of properties-> update and change
    instant3 = Instant.from_utc(2000, 1, 1, 3)
    with patch_current_time(instant3, keep_ticking=False):
        test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}, properties={'p': 'prop'}))
        assert test_thing.label == ''
        assert test_thing.location == ''
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map({'p': 'prop'})
        assert test_thing._last_update.instant == instant3
        assert test_thing._last_change.instant == instant3

    # second set of properties-> update
    instant4 = Instant.from_utc(2000, 1, 1, 4)
    with patch_current_time(instant4, keep_ticking=False):
        test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}, properties={'p': 'prop'}))
        assert test_thing.label == ''
        assert test_thing.location == ''
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map({'p': 'prop'})
        assert test_thing._last_update.instant == instant4
        assert test_thing._last_change.instant == instant3

    # initial set of label-> update and change
    instant5 = Instant.from_utc(2000, 1, 1, 5)
    with patch_current_time(instant5, keep_ticking=False):
        test_thing.process_event(MyThingUpdatedEvent(label='l1', configuration={'a': 'b'}, properties={'p': 'prop'}))
        assert test_thing.label == 'l1'
        assert test_thing.location == ''
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map({'p': 'prop'})
        assert test_thing._last_update.instant == instant5
        assert test_thing._last_change.instant == instant5

    # second set of label-> update
    instant6 = Instant.from_utc(2000, 1, 5, 6)
    with patch_current_time(instant6, keep_ticking=False):
        test_thing.process_event(MyThingUpdatedEvent(label='l1', configuration={'a': 'b'}, properties={'p': 'prop'}))
        assert test_thing.label == 'l1'
        assert test_thing.location == ''
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map({'p': 'prop'})
        assert test_thing._last_update.instant == instant6
        assert test_thing._last_change.instant == instant5

    # initial set of location-> update and change
    instant7 = Instant.from_utc(2000, 1, 5, 7)
    with patch_current_time(instant7, keep_ticking=False):
        test_thing.process_event(
            MyThingUpdatedEvent(location='my_loc', label='l1', configuration={'a': 'b'}, properties={'p': 'prop'})
        )
        assert test_thing.label == 'l1'
        assert test_thing.location == 'my_loc'
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map({'p': 'prop'})
        assert test_thing._last_update.instant == instant7
        assert test_thing._last_change.instant == instant7

    # second set of location-> update
    instant8 = Instant.from_utc(2000, 1, 5, 8)
    with patch_current_time(instant8, keep_ticking=False):
        test_thing.process_event(
            MyThingUpdatedEvent(location='my_loc', label='l1', configuration={'a': 'b'}, properties={'p': 'prop'})
        )
        assert test_thing.label == 'l1'
        assert test_thing.location == 'my_loc'
        assert test_thing.configuration == Map({'a': 'b'})
        assert test_thing.properties == Map({'p': 'prop'})
        assert test_thing._last_update.instant == instant8
        assert test_thing._last_change.instant == instant7


def test_thing_called_status_event(monkeypatch, ir: ItemRegistry, test_thing: Thing) -> None:
    monkeypatch.setattr(process_events_module, 'get_event', lambda x: x)

    ir.add_item(test_thing)
    test_thing.process_event = Mock()

    event = get_status_event('REMOVING')
    assert test_thing.name == event.name

    process_events_module.on_sse_event(event, oh_3=False)
    test_thing.process_event.assert_called_once_with(event)


def test_thing_called_updated_event(monkeypatch, ir: ItemRegistry, test_thing: Thing) -> None:
    monkeypatch.setattr(process_events_module, 'get_event', lambda x: x)

    ir.add_item(test_thing)
    test_thing.process_event = Mock()

    event = ThingUpdatedEvent('test_thing', 'new_type', 'new_label', '', channels=[], configuration={}, properties={})
    assert test_thing.name == event.name

    process_events_module.on_sse_event(event, oh_3=False)
    test_thing.process_event.assert_called_once_with(event)


def test_thing_handler_add_event(monkeypatch, ir: ItemRegistry) -> None:
    monkeypatch.setattr(process_events_module, 'get_event', lambda x: x)

    name = 'AddedThing'
    type = 'thing:type'
    label = 'my_label'
    location = 'my_loc'
    channels = [{'channel': 'data'}]
    configuration = {'my': 'config'}
    properties = {'my': 'properties'}

    event = ThingAddedEvent(name=name, thing_type=type, label=label, location=location, channels=channels,
                            configuration=configuration, properties=properties)
    process_events_module.on_sse_event(event, oh_3=False)

    thing = ir.get_item(name)
    assert isinstance(thing, Thing)
    assert thing.name == name
    assert thing.status == 'UNINITIALIZED'
    assert thing.status_detail == 'NONE'
    assert thing.label == label
    assert thing.location == location
    assert thing.configuration == Map(configuration)
    assert thing.properties == Map(properties)

    # ensure that everything gets overwritten
    thing.status = 'EXISTING_STATUS'
    thing.status_detail = 'EXISTING_STATUS_DETAUL'
    thing.label = 'EXISTING_LABEL'
    thing.location = 'EXISTING_LOCATION'
    thing.configuration = {'EXISTING': 'CONFIGURATION'}
    thing.properties = {'EXISTING': 'PROPERTIES'}

    event = ThingAddedEvent(name=name, thing_type=type, label=label, location=location, channels=channels,
                            configuration=configuration, properties=properties)
    process_events_module.on_sse_event(event, oh_3=False)

    thing = ir.get_item(name)
    assert isinstance(thing, Thing)
    assert thing.name == name
    assert thing.status == 'UNINITIALIZED'
    assert thing.status_detail == 'NONE'
    assert thing.label == label
    assert thing.location == location
    assert thing.configuration == Map(configuration)
    assert thing.properties == Map(properties)
