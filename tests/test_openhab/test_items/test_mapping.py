from HABApp.openhab.map_items import map_items


def test_exception():
    assert map_items('test', 'Number', 'asdf') is None
