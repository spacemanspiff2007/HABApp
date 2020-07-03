from HABApp.openhab.map_items import map_items
from HABApp.openhab.items import NumberItem


def test_exception():
    assert map_items('test', 'Number', 'asdf') is None


def test_number_unit_of_measurement():
    assert map_items('test1', 'Number:Length', '1.0 m')          == NumberItem('test', 1)
    assert map_items('test2', 'Number:Temperature', '2.0 °C')    == NumberItem('test', 2)
    assert map_items('test3', 'Number:Pressure', '3.0 hPa')      == NumberItem('test', 3)
    assert map_items('test4', 'Number:Speed', '4.0 km/h')        == NumberItem('test', 4)
    assert map_items('test5', 'Number:Intensity', '5.0 W/m2')    == NumberItem('test', 5)
    assert map_items('test6', 'Number:Dimensionless', '6.0')     == NumberItem('test', 6)
    assert map_items('test7', 'Number:Angle', '7.0 °')           == NumberItem('test', 7)
