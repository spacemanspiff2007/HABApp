import pytest
from immutables import Map

import HABApp
from HABApp.core.internals import HINT_ITEM_REGISTRY
from HABApp.openhab.events import ThingStatusInfoEvent, ThingUpdatedEvent
from HABApp.openhab.items import Thing
from HABApp.openhab.map_events import get_event
from pendulum import set_test_now, DateTime, UTC


@pytest.fixture(scope="function")
def test_thing(ir: HINT_ITEM_REGISTRY):
    set_test_now(DateTime(2000, 1, 1, tzinfo=UTC))
    thing = HABApp.openhab.items.Thing('test_thing')

    yield thing

    set_test_now()


def get_status_event(status: str) -> ThingStatusInfoEvent:
    data = {
        'topic': 'smarthome/things/test_thing/status',
        'payload': f'{{"status":"{status}","statusDetail":"NONE"}}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    return event


def test_thing_status_events(test_thing: Thing):

    assert test_thing.status == ''

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
    test_thing.process_event(get_status_event('asdf'))
    assert test_thing.status == 'asdf'
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)

    test_thing.process_event(get_status_event('NONE'))
    assert test_thing.status is None


def get_config_event(status) -> ThingStatusInfoEvent:
    data = {
        'topic': 'smarthome/things/test_thing/status',
        'payload': f'{{"status":"{status}","statusDetail":"NONE"}}',
        'type': 'ThingStatusInfoEvent'
    }
    event = get_event(data)
    assert isinstance(event, ThingStatusInfoEvent)
    return event


def test_thing_updated_event(test_thing: Thing):

    assert test_thing.properties == Map()
    assert test_thing.configuration == Map()

    # initial set of configuration -> update and change
    set_test_now(DateTime(2000, 1, 1, 1, tzinfo=UTC))
    test_thing.process_event(ThingUpdatedEvent(configuration={'a': 'b'}))
    assert test_thing.label == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map()
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)

    # second set of configuration -> update
    set_test_now(DateTime(2000, 1, 1, 2, tzinfo=UTC))
    test_thing.process_event(ThingUpdatedEvent(configuration={'a': 'b'}))
    assert test_thing.label == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map()
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 2, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 1, tzinfo=UTC)

    # initial set of properties-> update and change
    set_test_now(DateTime(2000, 1, 1, 3, tzinfo=UTC))
    test_thing.process_event(ThingUpdatedEvent(configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)

    # second set of properties-> update
    set_test_now(DateTime(2000, 1, 1, 4, tzinfo=UTC))
    test_thing.process_event(ThingUpdatedEvent(configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == ''
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 4, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 3, tzinfo=UTC)

    # initial set of label-> update and change
    set_test_now(DateTime(2000, 1, 1, 5, tzinfo=UTC))
    test_thing.process_event(ThingUpdatedEvent(label='l1', configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == 'l1'
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)

    # second set of label-> update
    set_test_now(DateTime(2000, 1, 1, 6, tzinfo=UTC))
    test_thing.process_event(ThingUpdatedEvent(label='l1', configuration={'a': 'b'}, properties={'p': 'prop'}))
    assert test_thing.label == 'l1'
    assert test_thing.configuration == Map({'a': 'b'})
    assert test_thing.properties == Map({'p': 'prop'})
    assert test_thing._last_update.dt == DateTime(2000, 1, 1, 6, tzinfo=UTC)
    assert test_thing._last_change.dt == DateTime(2000, 1, 1, 5, tzinfo=UTC)
