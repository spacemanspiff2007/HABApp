from HABApp.openhab.connection.plugins.plugin_things.file_writer.formatter_builder import (
    EmptyFormatter,
    LinkFormatter,
    MetadataFormatter,
    MultipleValueFormatterBuilder,
    ValueFormatterBuilder,
)


def test_value_formatter():
    b = ValueFormatterBuilder('test', '"{:s}"')

    # obj access
    class TestData1:
        test = 'asdf '

    f = b.create_formatter(TestData1)
    assert f.value == '"asdf"'

    class TestDataEmpty:
        test = ' '

    f = b.create_formatter(TestDataEmpty)
    assert isinstance(f, EmptyFormatter)
    assert f.value == ''


def test_multiple_value_formatter():
    b = MultipleValueFormatterBuilder('test', '"{:s}"', '({:s})')

    class TestData1:
        test = ('asdf ', ' bsdf')

    f = b.create_formatter(TestData1)
    assert f.value == '("asdf", "bsdf")'

    class TestDataEmpty:
        test = (' ', '', '    ')

    f = b.create_formatter(TestDataEmpty)
    assert isinstance(f, EmptyFormatter)
    assert f.value == ''
    assert f.len() == 0


def test_link_formatter():
    b = LinkFormatter()

    class TestData:
        link = 'my:link'
        metadata = {}

    f = b.create_formatter(TestData)
    assert f.value == 'channel = "my:link"'

    class TestData:
        link = 'my:link'
        metadata = {'key': 'value'}

    f = b.create_formatter(TestData)
    assert f.value == 'channel = "my:link",'

    class TestData:
        link = None
        metadata = {'key': 'value'}

    f = b.create_formatter(TestData)
    assert f.value == ''


def test_metadata_formatter():
    b = MetadataFormatter()

    class TestData:
        metadata = {'name': {'value': 'enabled', 'config': {}}}

    f = b.create_formatter(TestData)
    assert f.value == 'name="enabled"'

    class TestData:
        metadata = {
            'name1': {'value': 'enabled', 'config': {}},
            'name2': {'value': 'asdf', 'config': {'cfg1': 1}},
        }

    f = b.create_formatter(TestData)
    assert f.value == 'name1="enabled", name2="asdf" [cfg1=1]'


    class TestData:
        metadata = {
            'name2': {'value': 'asdf', 'config': {'cfg2': 1, 'cfg1': 'test'}},
            'name1': {'value': 'enabled', 'config': {}},
        }

    f = b.create_formatter(TestData)
    assert f.value == 'name1="enabled", name2="asdf" [cfg1="test", cfg2=1]'
