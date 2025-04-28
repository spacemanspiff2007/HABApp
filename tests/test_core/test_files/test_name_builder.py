from pathlib import Path

import pytest

from HABApp.core.files.name_builder import FileNameBuilder


def test_create() -> None:
    f = FileNameBuilder()

    with pytest.raises(ValueError) as e:
        f.create_name('asdf')
    assert str(e.value) == 'Nothing matched for path asdf'

    with pytest.raises(ValueError) as e:
        f.create_path('asdf')
    assert str(e.value) == 'Nothing matched for name asdf'

    f.add_folder('p1/', Path('as'), priority=1)

    assert not f.is_accepted_path('asd/asdf')
    assert not f.is_accepted_name('p2/asdf')

    assert f.is_accepted_path('as/asdf')
    assert f.is_accepted_name('p1/asdf')
    assert f.create_path('p1/asdf') == Path('as/asdf')
    assert f.create_name('as/asdf') == 'p1/asdf'

    f.add_folder('p1/', Path('as'), priority=2)

    with pytest.raises(ValueError) as e:
        f.create_name(Path('as/df').as_posix())
    assert str(e.value) == 'Multiple matches for path as/df: p1/df, p1/df'

    with pytest.raises(ValueError) as e:
        f.create_path('p1/df')
    assert str(e.value) == 'Multiple matches for name p1/df: as/df, as/df'


def test_get_names() -> None:
    f = FileNameBuilder()
    f.add_folder('p1/', Path('fa1'), priority=1)
    f.add_folder('z2/', Path('fz2'), priority=2)

    files = ['p1/', 'p1/a', 'p1/a', 'z2/', 'z2/f', 'z2/a', '???']
    target = ['z2/', 'z2/a', 'z2/f', 'p1/', 'p1/a', 'p1/a']

    assert list(f.get_names(files)) == target
    assert list(f.get_names(files, reverse=True)) == target[::-1]
