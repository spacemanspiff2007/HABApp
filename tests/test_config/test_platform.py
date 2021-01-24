from pathlib import Path

from HABApp.config import config_loader, default_logfile
from HABApp.config.platform_defaults import get_log_folder


def test_defaults():
    assert None is get_log_folder()
    assert Path('/log') == get_log_folder(Path('/log'))


def test_valid_yml(monkeypatch):
    monkeypatch.setattr(default_logfile, 'is_openhabian', lambda: True)
    monkeypatch.setattr(default_logfile, 'get_log_folder', lambda: Path('/platfrom/log/folder'))

    default = default_logfile.get_default_logfile()
    config_loader._yaml_param.load(default)
