from HABApp.util.functions import max, min


def test_none_remove() -> None:
    for func in (max, min):
        assert func(1, None) == 1
        assert func(None, None, default=2) == 2
        assert func([], default='asdf') == 'asdf'


def test_min() -> None:
    assert min(1, None) == 1
    assert min(2, 3, None) == 2

    assert min([1, None]) == 1
    assert min([2, 3, None]) == 2


def test_max() -> None:
    assert max(1, None) == 1
    assert max(2, 3, None) == 3

    assert max([1, None]) == 1
    assert max([2, 3, None]) == 3
