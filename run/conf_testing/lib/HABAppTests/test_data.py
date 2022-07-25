import copy
import datetime
import itertools

# we only support milliseconds on openHAB side
now = datetime.datetime.now()
now = now.replace(microsecond=now.microsecond // 1000 * 1000)

ITEM_STATE = {
    'Color': [(1, 2, 3), (2.0, 3.0, 4.0)],
    'Contact': ['OPEN', 'CLOSED'],
    'DateTime': [
        now,
        now + datetime.timedelta(10),
        now - datetime.timedelta(10),
    ],
    'Dimmer': [0, 100, 55.5],
    'Location': ["1,2,3", "-1.1,2.2,3.3"],
    'Number': [-111, 222, -13.13, 55.55],
    'Player': ["PLAY", "PAUSE", "REWIND", "FASTFORWARD"],
    'Rollershutter': [0, 100, 30.5],
    'String': ['A', 'B', 'C', '', 'öäüß'],
    'Switch': ['ON', 'OFF'],
}

ITEM_EVENTS = {
    'Switch': ['ON', 'OFF'],
    'Dimmer': ['ON', 'OFF'],
    'Color': ['ON', 'OFF'],
    'Rollershutter': ['UP', 'DOWN'],
}


def get_openhab_test_states(key) -> list:
    return list(copy.copy(ITEM_STATE[key]))


def get_openhab_test_events(key) -> list:
    return list(copy.copy(itertools.chain(ITEM_STATE[key], ITEM_EVENTS.get(key, []))))


def get_openhab_test_types() -> list:
    return list(set(itertools.chain(ITEM_STATE.keys(), ITEM_EVENTS.keys())))
