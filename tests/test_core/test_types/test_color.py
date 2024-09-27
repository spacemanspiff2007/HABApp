import pytest

from HABApp.core.types.color import HSB, RGB


def test_rgb() -> None:
    rgb = RGB(1, 2, 3)
    assert rgb.r == rgb.red == 1
    assert rgb.g == rgb.green == 2
    assert rgb.b == rgb.blue == 3

    assert rgb[0] == 1
    assert rgb['r'] == 1
    assert rgb['red'] == 1

    assert rgb[1] == 2
    assert rgb['g'] == 2
    assert rgb['green'] == 2

    assert rgb[2] == 3
    assert rgb['b'] == 3
    assert rgb['blue'] == 3

    r, g, b = rgb
    assert r == rgb.r
    assert g == rgb.g
    assert b == rgb.b

    assert tuple(rgb) == (rgb.r, rgb.g, rgb.b)

    assert str(rgb) == 'RGB(1, 2, 3)'
    assert rgb == RGB(1, 2, 3)
    assert rgb != RGB(9, 2, 3)
    assert rgb != RGB(1, 9, 3)
    assert rgb != RGB(1, 2, 9)


def test_rgb_create() -> None:
    for x in (-1, 256):
        with pytest.raises(ValueError):
            RGB(x, 2, 3)
        with pytest.raises(ValueError):
            RGB(1, x, 3)
        with pytest.raises(ValueError):
            RGB(1, 2, x)


def test_rgb_replace() -> None:
    rgb = RGB(1, 2, 3)
    assert rgb.replace(r=8) == RGB(8, 2, 3)
    assert rgb.replace(g=8) == RGB(1, 8, 3)
    assert rgb.replace(b=8) == RGB(1, 2, 8)

    assert rgb.replace(red=8)   == RGB(8, 2, 3)
    assert rgb.replace(green=8) == RGB(1, 8, 3)
    assert rgb.replace(blue=8)  == RGB(1, 2, 8)

    with pytest.raises(ValueError):
        rgb.replace(r=1, red=1)
    with pytest.raises(ValueError):
        rgb.replace(g=1, green=1)
    with pytest.raises(ValueError):
        rgb.replace(b=1, blue=1)


def test_rgb_hsb_compare() -> None:
    rgb = RGB(1, 2, 3)
    hsb = rgb.to_hsb()
    assert rgb == hsb
    assert hsb == rgb


def test_hsb() -> None:
    hsb = HSB(1, 2, 3)
    assert hsb.h == hsb.hue == 1
    assert hsb.s == hsb.saturation == 2
    assert hsb.b == hsb.brightness == 3

    assert hsb[0] == 1
    assert hsb['h'] == 1
    assert hsb['hue'] == 1

    assert hsb[1] == 2
    assert hsb['s'] == 2
    assert hsb['saturation'] == 2

    assert hsb[2] == 3
    assert hsb['b'] == 3
    assert hsb['brightness'] == 3

    h, s, b = hsb
    assert h == hsb.h
    assert s == hsb.s
    assert b == hsb.b

    assert tuple(hsb) == (hsb.h, hsb.s, hsb.b)

    assert str(hsb) == 'HSB(1.00, 2.00, 3.00)'
    assert hsb == HSB(1, 2, 3)
    assert hsb != HSB(9, 2, 3)
    assert hsb != HSB(1, 9, 3)
    assert hsb != HSB(1, 2, 9)


def test_hsb_create() -> None:
    with pytest.raises(ValueError):
        HSB(-1, 2, 3)
    with pytest.raises(ValueError):
        HSB(360.1, 2, 3)

    with pytest.raises(ValueError):
        HSB(1, -1, 3)
    with pytest.raises(ValueError):
        HSB(1, 100.1, 3)

    with pytest.raises(ValueError):
        HSB(1, 2, -1)
    with pytest.raises(ValueError):
        HSB(1, 2, 100.1)


def test_hsb_replace() -> None:
    hsb = HSB(1, 2, 3)
    assert hsb.replace(h=8) == HSB(8, 2, 3)
    assert hsb.replace(s=8) == HSB(1, 8, 3)
    assert hsb.replace(b=8) == HSB(1, 2, 8)

    assert hsb.replace(hue=8)        == HSB(8, 2, 3)
    assert hsb.replace(saturation=8) == HSB(1, 8, 3)
    assert hsb.replace(brightness=8) == HSB(1, 2, 8)

    with pytest.raises(ValueError):
        hsb.replace(h=1, hue=1)
    with pytest.raises(ValueError):
        hsb.replace(s=1, saturation=1)
    with pytest.raises(ValueError):
        hsb.replace(b=1, brightness=1)
