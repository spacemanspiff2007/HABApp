from HABApp.openhab.connection.plugins.plugin_things.str_builder import StrBuilder


def test_accessor():
    b = StrBuilder('MyText{thing_location}')
    assert b.get_str({'thing_location': '1'}) == 'MyText1'


def test_regex():
    b = StrBuilder(r'MyText{thing_location,(\d+)}')
    assert b.get_str({'thing_location': 'asdf123asdf'}) == 'MyText123'


def test_regex_replace():
    b = StrBuilder(r'MyText{thing_location,\w+?(\d+).+,\g<1>456}')
    assert b.get_str({'thing_location': 'asdf123asdf'}) == 'MyText123456'
