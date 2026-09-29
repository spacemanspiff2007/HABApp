from unittest.mock import Mock

from HABApp.core.internals import EventBus
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
from HABApp.openhab.items import GroupItem, StringItem


def test_item_group_members_sorted(ir, oh_interface) -> None:
    handler = OhItemRegistryHandler(ir)

    s1 = StringItem('d_str', initial_value='val_9', groups=frozenset(['grp_1']), event_bus=Mock(EventBus), interface=oh_interface)
    s2 = StringItem('a_str', groups=frozenset(['grp_1']), event_bus=Mock(EventBus), interface=oh_interface)
    s3 = StringItem('b_str', groups=frozenset(['grp_1']), event_bus=Mock(EventBus), interface=oh_interface)
    grp = GroupItem('grp_1', registry_handler=handler, event_bus=Mock(EventBus), interface=oh_interface)

    handler.add_to_registry(s1)
    handler.add_to_registry(s2)
    handler.add_to_registry(s3)
    handler.add_to_registry(grp)

    grp = GroupItem('grp_1', registry_handler=handler, event_bus=Mock(EventBus), interface=oh_interface)
    assert grp.members == (s2, s3, s1,)
