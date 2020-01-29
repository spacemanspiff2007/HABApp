import pytest

import HABApp
from HABApp.openhab.events import ThingStatusInfoEvent
from HABApp.openhab.items import Thing

from HABApp.openhab.map_events import get_event


@pytest.fixture(scope="function")
def test_thing():
    thing = HABApp.openhab.items.Thing('test_thing')
    HABApp.core.Items.set_item(thing)

    yield thing

    HABApp.core.Items.pop_item('test_thing')


def get_dict(status: str):
    return {
        'topic': 'smarthome/things/test_thing/status',
        'payload': f'{{"status":"{status}","statusDetail":"NONE"}}',
        'type': 'ThingStatusInfoEvent'
    }


def test_thing_status_events(test_thing: Thing):

    assert test_thing.status == ''
    e = get_event(get_dict('ONLINE'))
    assert isinstance(e, ThingStatusInfoEvent)
    test_thing.process_event(e)
    assert test_thing.status == 'ONLINE'

    e = get_event(get_dict('asdf'))
    assert isinstance(e, ThingStatusInfoEvent)
    test_thing.process_event(e)
    assert test_thing.status == 'asdf'

    e = get_event(get_dict('NONE'))
    assert isinstance(e, ThingStatusInfoEvent)
    test_thing.process_event(e)
    assert test_thing.status is None
