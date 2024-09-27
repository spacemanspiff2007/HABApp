from json import dumps

from msgspec.json import decode

from HABApp.openhab.definitions.rest.things import ThingResp


def test_thing_summary() -> None:
    _in = {
        'statusInfo': {
            'status': 'UNINITIALIZED',
            'statusDetail': 'NONE'
        },
        'editable': True,
        'label': 'Astronomische Sonnendaten',
        'UID': 'astro:sun:d522ba4b56',
        'thingTypeUID': 'astro:sun'
    }

    thing = decode(dumps(_in), type=ThingResp)

    assert thing.editable is True
    assert thing.uid == 'astro:sun:d522ba4b56'
    assert thing.label == 'Astronomische Sonnendaten'
    assert thing.thing_type == 'astro:sun'

    assert thing.status.status == 'UNINITIALIZED'
    assert thing.status.detail == 'NONE'


def test_thing_full() -> None:
    _in = {
        'channels': [
            {
                'linkedItems': [
                    'LinkedItem1',
                    'LinkedItem2'
                ],
                'uid': 'astro:sun:d522ba4b56:rise#start',
                'id': 'rise#start',
                'channelTypeUID': 'astro:start',
                'itemType': 'DateTime',
                'kind': 'STATE',
                'label': 'Startzeit',
                'description': 'Die Startzeit des Ereignisses',
                'defaultTags': [],
                'properties': {},
                'configuration': {
                    'offset': 0
                },
            },
            {
                'linkedItems': [],
                'uid': 'astro:sun:d522ba4b56:eveningNight#duration',
                'id': 'eveningNight#duration',
                'channelTypeUID': 'astro:duration',
                'itemType': 'Number:Time',
                'kind': 'STATE',
                'label': 'Dauer',
                'description': 'Die Dauer des Ereignisses',
                'defaultTags': [],
                'properties': {},
                'configuration': {}
            },
            {
                'linkedItems': [],
                'uid': 'astro:sun:d522ba4b56:eclipse#event',
                'id': 'eclipse#event',
                'channelTypeUID': 'astro:sunEclipseEvent',
                'kind': 'TRIGGER',
                'label': 'Sonnenfinsternisereignis',
                'description': 'Sonnenfinsternisereignis',
                'defaultTags': [],
                'properties': {},
                'configuration': {
                    'offset': 0
                }
            },
        ],
        'statusInfo': {
            'status': 'UNINITIALIZED',
            'statusDetail': 'NONE'
        },
        'editable': True,
        'label': 'Astronomische Sonnendaten',
        'configuration': {
            'useMeteorologicalSeason': False,
            'interval': 300,
            'geolocation': '46.123,2.123'
        },
        'properties': {},
        'UID': 'astro:sun:d522ba4b56',
        'thingTypeUID': 'astro:sun'
    }

    thing = decode(dumps(_in), type=ThingResp)

    c0, c1, c2 = thing.channels

    assert c0.linked_items == ['LinkedItem1', 'LinkedItem2']
    assert c0.configuration == {'offset': 0}

    assert c1.linked_items == []
    assert c1.configuration == {}

    assert thing.status.status == 'UNINITIALIZED'
    assert thing.status.detail == 'NONE'

    assert thing.editable is True
    assert thing.label == 'Astronomische Sonnendaten'

    assert thing.configuration == {'useMeteorologicalSeason': False, 'interval': 300, 'geolocation': '46.123,2.123'}
    assert thing.properties == {}

    assert thing.uid == 'astro:sun:d522ba4b56'
    assert thing.thing_type == 'astro:sun'
