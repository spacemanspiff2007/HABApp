from HABApp.openhab.connection.plugins.plugin_things.file_writer.formatter import FormatterScope
from HABApp.openhab.connection.plugins.plugin_things.file_writer.formatter_builder import ValueFormatter


def test_scope():
    assert FormatterScope(field_names=('a', 'd1')).get_lines() == []

    s = FormatterScope(field_names=('a', 'b', 'b1', 'c', 'd', 'd1'))
    s.lines = [
        {'a': ValueFormatter('val_1a'), 'b': ValueFormatter('val_1_bbbbb'), 'c': ValueFormatter('val_1 __cc__'), },
        {'a': ValueFormatter('val_2__a'), 'b': ValueFormatter('val_2b'), 'c': ValueFormatter('val_2 ____cc__'), },
    ]

    assert s.get_lines() == [
        'val_1a      val_1_bbbbb   val_1 __cc__',
        'val_2__a    val_2b        val_2 ____cc__'
    ]


def test_scope_missing():
    s = FormatterScope(field_names=('a', 'c'))
    s.lines = [
        {'a': ValueFormatter('val_1a'), 'c': ValueFormatter('val_1 __cc__'), },
        {'a': ValueFormatter('val_2__a'), 'b': ValueFormatter('val_2b'), 'c': ValueFormatter('val_2 ____cc__'), },
    ]

    assert s.get_lines() == [
        'val_1a      val_1 __cc__',
        'val_2__a    val_2 ____cc__'
    ]


def test_scope_skip():
    s = FormatterScope(field_names=('a', 'b', 'b1', 'c', 'd', 'd1'), skip_alignment=('b1', 'd', 'd1'))
    s.lines = [
        {'a': ValueFormatter('val_1a'), 'b': ValueFormatter('val_1_bbbbb'), 'b1': ValueFormatter('{'),
         'c': ValueFormatter('val_1 __cc__'), 'd': ValueFormatter('val_1 __d'), 'd1': ValueFormatter('}'), },
        {'a': ValueFormatter('val_2__a'), 'b': ValueFormatter('val_2b'), 'b1': ValueFormatter('{'),
         'c': ValueFormatter('val_2 ____cc__'), 'd': ValueFormatter('val_1 __d___'), 'd1': ValueFormatter('}'), },
    ]

    assert s.get_lines() == [
        'val_1a      val_1_bbbbb   {val_1 __cc__    val_1 __d   }',
        'val_2__a    val_2b        {val_2 ____cc__  val_1 __d___}'
    ]


def test_scope_min_width():
    s = FormatterScope(field_names=('a', 'b', 'b1', 'c', 'd', 'd1', ), min_width={'a': 15})
    s.lines = [
        {'a': ValueFormatter('val_1a'), 'b': ValueFormatter('val_1_bbbbb'), 'c': ValueFormatter('val_1 __cc__'), },
        {'a': ValueFormatter('val_2__a'), 'b': ValueFormatter('val_2b'), 'c': ValueFormatter('val_2 ____cc__'), },
    ]

    assert s.get_lines() == [
        'val_1a         val_1_bbbbb   val_1 __cc__',
        'val_2__a       val_2b        val_2 ____cc__'
    ]
