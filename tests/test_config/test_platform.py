from pathlib import Path

from HABApp.config.platform_defaults import get_log_folder


def test_defaults():
    assert None is get_log_folder()
    assert Path('/log') == get_log_folder(Path('/log'))
