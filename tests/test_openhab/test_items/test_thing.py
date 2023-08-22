from typing import List, Dict, Any
from unittest.mock import Mock

import pytest
from immutables import Map
from pendulum import set_test_now, DateTime, UTC

import HABApp
from HABApp.core.internals import ItemRegistry
from HABApp.openhab import process_events as process_events_module
from HABApp.openhab.events import ThingStatusInfoEvent, ThingUpdatedEvent, ThingAddedEvent
from HABApp.openhab.items import Thing
from HABApp.openhab.map_events import get_event


@pytest.fixture(scope="function")
def test_thing(ir: ItemRegistry):
    set_test_now(DateTime(2000, 1, 1, tzinfo=UTC))
    thing = HABApp.openhab.items.Thing('test_thing')

    yield thing

    set_test_now()


def get_status_event(status: str) -> ThingStatusInfoEvent:
    data = {
        'topic': 'openhab/things/test_thing/status',
        'payload': f'{{"status":"{status}","statusDetail":"NONE"}}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    return event


def test_thing_status_events(test_thing: Thing):

    assert test_thing.status == 'UNINITIALIZED'

    # initial set -> update and change
    set_test_now(DateTime(2000, 1, 1, 1, tzinfo=UTC))
    test_thing.process_event(get_status_event('ONLINE'))
    assert test_thing.status == 'ONLINE'
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)

    # second set -> update
    set_test_now(DateTime(2000, 1, 1, 2, tzinfo=UTC))
    test_thing.process_event(get_status_event('ONLINE'))
    assert test_thing.status == 'ONLINE'
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 2, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)

    # third set -> update & change
    set_test_now(DateTime(2000, 1, 1, 3, tzinfo=UTC))
    test_thing.process_event(get_status_event('INITIALIZING'))
    assert test_thing.status == 'INITIALIZING'
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)


def test_thing_updated_event(test_thing: Thing):

    class MyThingUpdatedEvent(ThingUpdatedEvent):
        def __init__(self, name: str = '', thing_type: str = '', label: str = '', location='',
                     channels: List[Dict[str, Any]] = [],
                     configuration: Dict[str, Any] = {}, properties: Dict[str, str] = {}):
            super().__init__(name, thing_type, label, location, channels, configuration, properties)

    assert test_thing.properties == Map()
    assert test_thing.configuration == Map()

    # initial set of configuration -> update and change
    set_test_now(DateTime(2000, 1, 1, 1, tzinfo=UTC))
    test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}))
    assert test_thing.label == ''
    assert test_thing.location == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map()
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)

    # second set of configuration -> update
    set_test_now(DateTime(2000, 1, 1, 2, tzinfo=UTC))
    test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}))
    assert test_thing.label == ''
    assert test_thing.location == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map()
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 2, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)

    # initial set of properties-> update and change
    set_test_now(DateTime(2000, 1, 1, 3, tzinfo=UTC))
    test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == ''
    assert test_thing.location == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)

    # second set of properties-> update
    set_test_now(DateTime(2000, 1, 1, 4, tzinfo=UTC))
    test_thing.process_event(MyThingUpdatedEvent(configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == ''
    assert test_thing.location == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 4, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)

    # initial set of label-> update and change
    set_test_now(DateTime(2000, 1, 1, 5, tzinfo=UTC))
    test_thing.process_event(MyThingUpdatedEvent(label='l1', configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == 'l1'
    assert test_thing.location == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)

    # second set of label-> update
    set_test_now(DateTime(2000, 1, 1, 6, tzinfo=UTC))
    test_thing.process_event(MyThingUpdatedEvent(label='l1', configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == 'l1'
    assert test_thing.location == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 6, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)

    # initial set of location-> update and change
    set_test_now(DateTime(2000, 1, 1, 5, tzinfo=UTC))
    test_thing.process_event(
        MyThingUpdatedEvent(location='my_loc', label='l1', configuration={'a': 'b'}, properties={'p': 'prop'})
    )
    assert test_thing.label == 'l1'
    assert test_thing.location == 'my_loc'
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)

    # second set of location-> update
    set_test_now(DateTime(2000, 1, 1, 6, tzinfo=UTC))
    test_thing.process_event(
        MyThingUpdatedEvent(location='my_loc', label='l1', configuration={'a': 'b'}, properties={'p': 'prop'})
    )
    assert test_thing.label == 'l1'
    assert test_thing.location == 'my_loc'
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 6, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)


def test_thing_called_status_event(monkeypatch, ir: ItemRegistry, test_thing: Thing):
    monkeypatch.setattr(process_events_module, 'get_event', lambda x: x)

    ir.add_item(test_thing)
    test_thing.process_event = Mock()

    event = get_status_event('REMOVING')
    assert test_thing.name == event.name

    process_events_module.on_sse_event(event, oh_3=False)
    test_thing.process_event.assert_called_once_with(event)


def test_thing_called_updated_event(monkeypatch, ir: ItemRegistry, test_thing: Thing):
    monkeypatch.setattr(process_events_module, 'get_event', lambda x: x)

    ir.add_item(test_thing)
    test_thing.process_event = Mock()

    event = ThingUpdatedEvent('test_thing', 'new_type', 'new_label', '', channels=[], configuration={}, properties={})
    assert test_thing.name == event.name

    process_events_module.on_sse_event(event, oh_3=False)
    test_thing.process_event.assert_called_once_with(event)


def test_thing_handler_add_event(monkeypatch, ir: ItemRegistry):
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
