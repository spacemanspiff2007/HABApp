import pytest
import HABApp.openhab.items
from HABApp.openhab.items import GroupItem, StringItem
from HABApp.openhab.item_to_reg import add_to_registry


@pytest.mark.parametrize('cls', [
    getattr(HABApp.openhab.items, i) for i in dir(HABApp.openhab.items) if i[0] != '_' and i[0].isupper()
])
def test_item_has_name(cls):
    # this test ensure that all openHAB items inherit from OpenhabItem
    c = cls('asdf')
    assert c.name == 'asdf'
    if cls is not HABApp.openhab.items.Thing:
        assert isinstance(c, HABApp.openhab.items.OpenhabItem)


def test_item_group_members_sorted():
    add_to_registry(StringItem('d_str', initial_value='val_9', groups=frozenset(['grp_1'])))
    add_to_registry(StringItem('a_str', groups=frozenset(['grp_1'])))
    add_to_registry(StringItem('b_str', groups=frozenset(['grp_1'])))
    add_to_registry(GroupItem('grp_1'))

    grp = GroupItem.get_item('grp_1')
    assert grp.members == (
        StringItem.get_item('a_str'),
        StringItem.get_item('b_str'),
        StringItem.get_item('d_str'),
    )
