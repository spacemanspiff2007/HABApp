import pytest

import HABApp.openhab.items


@pytest.mark.parametrize('cls', [
    getattr(HABApp.openhab.items, i) for i in dir(HABApp.openhab.items) if i[0] != '_' and i[0].isupper()
])
def test_item_has_name(cls):
    # this test ensure that all openHAB items inherit from OpenhabItem
    c = cls('asdf')
    assert c.name == 'asdf'
    if cls is not HABApp.openhab.items.Thing:
        assert isinstance(c, HABApp.openhab.items.OpenhabItem)
