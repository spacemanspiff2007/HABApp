from unittest.mock import Mock

import pytest

import HABApp.util.listener_groups
from HABApp.core.items.base_valueitem import BaseItem
from HABApp.util import EventListenerGroup
from HABApp.util.listener_groups.listener_groups import EventListenerCreator, ListenerCreatorNotFoundError


class PatchedBaseItem(BaseItem):
    NAME = 'PatchedBaseItem'

    def __init__(self):
        super().__init__(PatchedBaseItem.NAME)

    listener = Mock()
    listen_event = Mock(return_value=listener)

    no_x_watch = Mock()
    no_x_watch.listen_event = Mock(return_value=listener)
    watch_change = Mock(return_value=no_x_watch)
    watch_update = Mock(return_value=no_x_watch)

    def reset(self):
        self.listener.reset_mock()
        self.listen_event.reset_mock()
        self.no_x_watch.reset_mock()
        self.watch_change.reset_mock()
        self.watch_update.reset_mock()


def patched_item() -> BaseItem:
    item = PatchedBaseItem()
    item.reset()
    return item


def test_not_found():
    msg = 'ListenerCreator for "asdf" not found!'

    g = EventListenerGroup()

    with pytest.raises(ListenerCreatorNotFoundError) as e:
        g.activate_listener('asdf')
    assert str(e.value) == msg

    with pytest.raises(ListenerCreatorNotFoundError) as e:
        g.deactivate_listener('asdf')
    assert str(e.value) == msg

    g.add_listener(patched_item(), Mock(), object(), alias='asdf')
    g.activate_listener('asdf')
    g.deactivate_listener('asdf')

    g.add_listener(patched_item(), Mock(), object())
    g.activate_listener('PatchedBaseItem')
    g.deactivate_listener('PatchedBaseItem')


@pytest.mark.parametrize('func', ('add_listener', 'add_no_update_watcher', 'add_no_change_watcher'))
def test_activate_deactivate(func):
    g = EventListenerGroup()
    item = patched_item()
    cb = object()
    p1 = object()

    def assert_called_once():
        if func == 'add_listener':
            item.listen_event.assert_called_once_with(cb, p1)
        else:
            if func == 'add_no_change_watcher':
                item.watch_change.assert_called_once_with(p1)
            else:
                item.watch_update.assert_called_once_with(p1)
            item.no_x_watch.listen_event.assert_called_once_with(cb)

    getattr(g, func)(item, cb, p1)

    assert not g.active

    g.listen()

    assert g.active
    assert_called_once()

    assert g.active
    assert_called_once()

    g.cancel()

    assert not g.active
    item.listener.cancel.assert_called_once_with()

    assert not g.active
    item.listener.cancel.assert_called_once_with()


def test_activate():
    g = EventListenerGroup()
    g._items['a'] = m = Mock()

    m.active = True
    assert not g.activate_listener('a')
    m.listen.assert_not_called()

    m.active = False
    assert g.activate_listener('a')
    m.listen.assert_not_called()

    m.active = False
    g.listen()
    m.listen.assert_called_once_with()

    assert g.activate_listener('a')
    assert m.active
    assert len(m.listen.mock_calls) == 2


def test_listen_add(monkeypatch):
    m = Mock()
    monkeypatch.setattr(
        HABApp.util.listener_groups.listener_groups, EventListenerCreator.__name__, Mock(return_value=m))

    item = patched_item()
    cb = object()
    p1 = object()

    g = EventListenerGroup()
    g.listen()

    g.add_listener(item, cb, p1)
    m.listen.assert_called_once_with()
