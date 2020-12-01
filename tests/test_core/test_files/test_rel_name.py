from pathlib import Path

import pytest

import HABApp
from HABApp.core.files import name_from_path, path_from_name


@pytest.fixture
def cfg(monkeypatch):
    monkeypatch.setattr(HABApp.config.CONFIG.directories, 'rules', Path('c:/HABApp/my_rules/'))
    monkeypatch.setattr(HABApp.config.CONFIG.directories, 'config', Path('c:/HABApp/my_config/'))
    monkeypatch.setattr(HABApp.config.CONFIG.directories, 'param', Path('c:/HABApp/my_param/'))

    yield None


def cmp(path: Path, name: str):
    assert name_from_path(path) == name
    assert path_from_name(name) == path


def test_from_path(cfg):
    cmp(Path('c:/HABApp/my_rules/rule.py'),     'rules/rule.py')
    cmp(Path('c:/HABApp/my_config/params.yml'), 'configs/params.yml')
    cmp(Path('c:/HABApp/my_param/cfg.yml'),     'params/cfg.yml')

    cmp(Path('c:/HABApp/my_rules/my_folder1/folder2/rule.py'), 'rules/my_folder1/folder2/rule.py')
    cmp(Path('c:/HABApp/my_config/my_folder2/cfg.yml'),        'configs/my_folder2/cfg.yml')
    cmp(Path('c:/HABApp/my_param/my_folder3/cfg.yml'),         'params/my_folder3/cfg.yml')


def test_err(cfg):
    with pytest.raises(ValueError):
        name_from_path(Path('c:/HABApp/rules/rule.py'))
