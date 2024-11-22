from HABApp.openhab.connection.handler import convert_to_oh_type


def test_convert_to_oh_type() -> None:
    assert convert_to_oh_type(1 / 10 ** 3) == '0.001'
    assert convert_to_oh_type(1 / 10 ** 6) == '0.000001'
    assert convert_to_oh_type(1 / 10 ** 9) == '0.000000001'

    assert convert_to_oh_type(1.234 / 10 ** 3) == '0.001234'
    assert convert_to_oh_type(1.234 / 10 ** 6) == '0.000001234'
    assert convert_to_oh_type(1.234 / 10 ** 9) == '0.000000001234'
