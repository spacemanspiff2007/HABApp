from HABApp.util.fade.fade import Fade


def test_setup():
    f = Fade().setup(0, 10, 10)
    assert f._fade_factor == 1
    assert f._step_duration == 1

    f = Fade().setup(0, 10, 20)
    assert f._fade_factor == 0.5
    assert f._step_duration == 2

    f = Fade().setup(0, 10, 5)
    assert f._fade_factor == 2
    assert f._step_duration == 0.5

    f = Fade().setup(0, 10, 2)
    assert f._fade_factor == 5
    assert f._step_duration == 0.2

    f = Fade().setup(0, 20, 1)
    assert f._fade_factor == 20
    assert f._step_duration == 0.2

    f = Fade().setup(0, 100, 10)
    assert f._fade_factor == 10
    assert f._step_duration == 0.2

    f = Fade().setup(0, 100, 10, min_step_duration=2)
    assert f._fade_factor == 10
    assert f._step_duration == 2


def test_values():
    f = Fade().setup(0, 10, 5, now=10)
    assert f.get_value(11) == 2
    assert f.get_value(12) == 4
    assert f.get_value(13) == 6
    assert f.get_value(14) == 8
    assert not f.is_finished
    f.get_value(14.99)
    assert not f.is_finished

    for i in range(15, 30):
        assert f.get_value(i) == 10
        assert f.is_finished
