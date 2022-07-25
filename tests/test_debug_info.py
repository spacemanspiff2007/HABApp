from HABApp.__debug_info__ import get_debug_info


def test_debug_info():
    info = get_debug_info()

    for line in info.splitlines():
        if ':' in line:
            assert not line.strip().endswith(':')
