from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
from HABApp.openhab.items import GroupItem, StringItem


def test_item_group_members_sorted(ir) -> None:
    handler = OhItemRegistryHandler(ir)

    handler.add_to_registry(StringItem('d_str', initial_value='val_9', groups=frozenset(['grp_1'])))
    handler.add_to_registry(StringItem('a_str', groups=frozenset(['grp_1'])))
    handler.add_to_registry(StringItem('b_str', groups=frozenset(['grp_1'])))
    handler.add_to_registry(GroupItem('grp_1', registry_handler=handler))

    grp = GroupItem.get_item('grp_1')
    assert grp.members == (
        StringItem.get_item('a_str'),
        StringItem.get_item('b_str'),
        StringItem.get_item('d_str'),
    )
