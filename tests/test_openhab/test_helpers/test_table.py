from HABApp.openhab.definitions.helpers.log_table import Column, Table


def test_col() -> None:
    col = Column('my heading', wrap=40)
    col.add(['asdf', 'def', '23456trhrethtre', 'ghdrhtrezertztre', 'adfsdsf'])
    assert col.count_lines(0) == 2
    assert col.format_entry(0, 2) == [
        'asdf, def, 23456trhrethtre, ghdrhtrezertztre',
        'adfsdsf                                     '
    ]


def test_table() -> None:
    table = Table('my heading')
    c1 = table.add_column('col1')
    c2 = table.add_column('col2')

    c1.add('12')
    c1.add(345)
    c1.add(23)

    c2.add('asdf')
    c2.add('ljkäöjio')
    c2.add('jfhgf')

    assert table.get_lines() == [
        '+-----------------+',
        '|   my heading    |',
        '+------+----------+',
        '| col1 |   col2   |',
        '+------+----------+',
        '| 12   | asdf     |',
        '|  345 | ljkäöjio |',
        '|   23 | jfhgf    |',
        '+------+----------+'
    ]

    assert table.get_lines(sort_columns=['col2']) == [
        '+-----------------+',
        '|   my heading    |',
        '+------+----------+',
        '| col1 |   col2   |',
        '+------+----------+',
        '| 12   | asdf     |',
        '|   23 | jfhgf    |',
        '|  345 | ljkäöjio |',
        '+------+----------+'
    ]


def test_wrap() -> None:
    table = Table('my heading')
    c1 = table.add_column('col1')
    c2 = table.add_column('col2', wrap=20)

    c1.add('12')
    c1.add(345)

    c2.add(['asdfasdfasdf', 'defdefdef', 'adfiopfafds', 'jkdfsj'])
    c2.add('ljkäöjio')

    assert table.get_lines() == [
        '+--------------------------------+',
        '|           my heading           |',
        '+------+-------------------------+',
        '| col1 |          col2           |',
        '+------+-------------------------+',
        '| 12   | asdfasdfasdf, defdefdef |',
        '|      | adfiopfafds, jkdfsj     |',
        '|  345 | ljkäöjio                |',
        '+------+-------------------------+'
    ]
