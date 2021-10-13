from unittest.mock import Mock

from HABApp.core.events import AllEvents
from HABApp.util import EventListenerGroup


def test_listen():
    item1 = Mock()
    item1.listen_event = Mock()
    item2 = Mock()
    item2.listen_event = Mock()

    cb = Mock(name='cb_mock')

    grp = EventListenerGroup(cb)
    grp.add_listener(item1)
    item1.listen_event.assert_not_called()

    # Assert that multiple calls will only create the listener once
    for i in range(5):
        grp.listen()
        item1.listen_event.assert_called_once_with(cb, AllEvents)

    assert grp.active

    grp.add_listener(item2)
    item1.listen_event.assert_called_once_with(cb, AllEvents)
    item2.listen_event.assert_called_once_with(cb, AllEvents)

    objs = grp._subs.copy()
    assert len(objs) == 2
    for o in objs:
        assert 'cancel' not in o.__dir__()

    grp.cancel()
    assert not grp.active

    for o in objs:
        cancel = o.cancel
        assert isinstance(cancel, Mock)
        cancel.assert_called_once_with()

    assert grp._subs == []


def test_overwrite_defaults():
    item1 = Mock()
    item1.listen_event = Mock()

    default_cb = Mock(name='cb_default')
    grp = EventListenerGroup(default_cb)

    cb, f = Mock(), Mock()
    grp.add_listener(item1, cb, f)

    item1.listen_event.assert_not_called()

    # Assert that multiple calls will only create the listener once
    for i in range(5):
        grp.listen()
        item1.listen_event.assert_called_once_with(cb, f)
    assert grp.active
