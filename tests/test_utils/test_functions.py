import pytest

from HABApp.util.functions import hsb_to_rgb, max, min, rgb_to_hsb


def test_none_remove():
    for func in (max, min):
        assert func(1, None) == 1
        assert func(None, None, default=2) == 2
        assert func([], default='asdf') == 'asdf'


def test_min():
    assert min(1, None) == 1
    assert min(2, 3, None) == 2

    assert min([1, None]) == 1
    assert min([2, 3, None]) == 2


def test_max():
    assert max(1, None) == 1
    assert max(2, 3, None) == 3

    assert max([1, None]) == 1
    assert max([2, 3, None]) == 3


@pytest.mark.parametrize("rgb,hsv", [
    ((224, 201, 219), (313.04,  10.27, 87.84)),
    ((  0, 201, 219), (184.93, 100.00, 85.88)),
    ((128, 138,  33), ( 65.71,  76.09, 54.12)),
    ((  0,   0,   0), (     0,      0,     0)),
])
def test_rgb_to_hsv(rgb, hsv):
    assert hsv == rgb_to_hsb(*rgb)


@pytest.mark.parametrize("hsv,rgb", [
    (( 75,  75,  75), (155, 191,  48)),
    ((150,  40, 100), (153, 255, 204)),
    ((234,  46,  72), ( 99, 108, 184)),
    ((  0, 100, 100), (255,   0,   0)),
    ((  0,   0,   0), (  0,   0,   0)),
])
def test_hsv_to_rgb(hsv, rgb):
    assert rgb == hsb_to_rgb(*hsv)
