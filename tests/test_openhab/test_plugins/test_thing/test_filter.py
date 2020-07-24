from HABApp.openhab.connection_logic.plugin_things.filters import ThingFilter, apply_filters


def test_thing_filter():
    f = ThingFilter('thing_label', 'asdfasdf')
    assert f.matches({'label': 'ASDFASDF'}, True)
    assert f.matches({'label': 'ASDFASDF'}, False)

    f = ThingFilter('thing_label', r'\d+')
    assert not f.matches({'label': 'asdf1234'}, True)
    assert not f.matches({'label': 'asdf1234'}, False)

    f = ThingFilter('thing_label', r'asdf\d+')
    assert f.matches({'label': 'asdf1234'}, True)
    assert f.matches({'label': 'asdf1234'}, False)


def test_filters():
    data = [{'label': '1'}, {'label': '2'}, {'label': 'a'}, {'label': 'b'}, ]
    assert list(apply_filters([ThingFilter('thing_label', r'\d+')], data, True)) == [{'label': '1'}, {'label': '2'}]
    assert list(apply_filters([ThingFilter('thing_label', r'\d+')], data, False)) == [{'label': '1'}, {'label': '2'}]

    assert list(apply_filters([ThingFilter('thing_label', 'no_match')], data, True)) == []
    assert list(apply_filters([ThingFilter('thing_label', 'no_match')], data, False)) == []
