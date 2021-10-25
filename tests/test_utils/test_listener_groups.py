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


def test_change():
    item1 = Mock()
    item1_ret = Mock()
    item1.watch_change = Mock(return_value=item1_ret)
    item2 = Mock()
    item2_ret = Mock()
    item2.watch_change = Mock(return_value=item2_ret)

    cb = Mock(name='cb_mock')

    grp = EventListenerGroup(cb, default_seconds=20)
    grp.add_no_change_watcher(item1, seconds=30)
    item1.watch_change.assert_not_called()
    item2.watch_change.assert_not_called()

    # Assert that multiple calls will only create the listener once
    for i in range(5):
        grp.listen()
        item1.watch_change.assert_called_once_with(30)
        item1_ret.listen_event.assert_called_once_with(cb)
        item2.watch_change.assert_not_called()

    assert grp.active

    # ensure that the watcher is added immediately when we are active
    grp.add_no_change_watcher(item2)
    item1.watch_change.assert_called_once_with(30)
    item1_ret.listen_event.assert_called_once_with(cb)
    item2.watch_change.assert_called_once_with(20)
    item2_ret.listen_event.assert_called_once_with(cb)

    # check that the cancel gets cleaned properly
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


def test_update():
    item1 = Mock()
    item1_ret = Mock()
    item1.watch_update = Mock(return_value=item1_ret)
    item2 = Mock()
    item2_ret = Mock()
    item2.watch_update = Mock(return_value=item2_ret)

    cb = Mock(name='cb_mock')

    grp = EventListenerGroup(cb, default_seconds=20)
    grp.add_no_update_watcher(item1, seconds=30)
    item1.watch_update.assert_not_called()
    item2.watch_update.assert_not_called()

    # Assert that multiple calls will only create the listener once
    for i in range(5):
        grp.listen()
        item1.watch_update.assert_called_once_with(30)
        item1_ret.listen_event.assert_called_once_with(cb)
        item2.watch_update.assert_not_called()

    assert grp.active

    # ensure that the watcher is added immediately when we are active
    grp.add_no_update_watcher(item2)
    item1.watch_update.assert_called_once_with(30)
    item1_ret.listen_event.assert_called_once_with(cb)
    item2.watch_update.assert_called_once_with(20)
    item2_ret.listen_event.assert_called_once_with(cb)

    # check that the cancel gets cleaned properly
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
