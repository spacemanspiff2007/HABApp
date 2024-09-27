from pathlib import Path

import pytest

from HABApp.core.files.folders import add_folder, get_name, get_path, get_prefixes
from HABApp.core.files.folders.folders import FOLDERS


@pytest.fixture()
def cfg():
    FOLDERS.clear()
    add_folder('rules/', Path('c:/HABApp/my_rules/'), 0)
    add_folder('configs/', Path('c:/HABApp/my_config/'), 10)
    add_folder('params/', Path('c:/HABApp/my_param/'), 20)

    yield None

    FOLDERS.clear()


def cmp(path: Path, name: str) -> None:
    assert get_name(path) == name
    assert get_path(name) == path


def test_prefix_sort(cfg) -> None:
    assert get_prefixes() == ['params/', 'configs/', 'rules/']
    add_folder('params1/', Path('c:/HABApp/my_para1m/'), 50)
    assert get_prefixes() == ['params1/', 'params/', 'configs/', 'rules/']


def test_from_path(cfg) -> None:
    cmp(Path('c:/HABApp/my_rules/rule.py'),     'rules/rule.py')
    cmp(Path('c:/HABApp/my_config/params.yml'), 'configs/params.yml')
    cmp(Path('c:/HABApp/my_param/cfg.yml'),     'params/cfg.yml')

    cmp(Path('c:/HABApp/my_rules/my_folder1/folder2/rule.py'), 'rules/my_folder1/folder2/rule.py')
    cmp(Path('c:/HABApp/my_config/my_folder2/cfg.yml'),        'configs/my_folder2/cfg.yml')
    cmp(Path('c:/HABApp/my_param/my_folder3/cfg.yml'),         'params/my_folder3/cfg.yml')


def test_err(cfg) -> None:
    with pytest.raises(ValueError):
        get_name(Path('c:/HABApp/rules/rule.py'))


def test_mixed() -> None:
    FOLDERS.clear()
    add_folder('rules/', Path('c:/HABApp/rules'), 1)
    add_folder('configs/', Path('c:/HABApp/rules/my_config'), 2)
    add_folder('params/', Path('c:/HABApp/rules/my_param'), 3)

    cmp(Path('c:/HABApp/rules/rule.py'),              'rules/rule.py')
    cmp(Path('c:/HABApp/rules/my_config/params.yml'), 'configs/params.yml')
    cmp(Path('c:/HABApp/rules/my_param/cfg.yml'),     'params/cfg.yml')

    FOLDERS.clear()
    add_folder('rules/', Path('c:/HABApp/rules'), 1)
    add_folder('configs/', Path('c:/HABApp/rules/my_cfg'), 2)
    add_folder('params/', Path('c:/HABApp/rules/my_param'), 3)

    cmp(Path('c:/HABApp/rules/rule.py'),           'rules/rule.py')
    cmp(Path('c:/HABApp/rules/my_cfg/params.yml'), 'configs/params.yml')
    cmp(Path('c:/HABApp/rules/my_param/cfg.yml'),  'params/cfg.yml')
