from inspect import getmembers, isclass
from pathlib import Path

from pydantic import BaseModel

import HABApp.config.models
from HABApp.config import CONFIG
from easyconfig import yaml


def test_sample_yaml(pytestconfig):
    file = pytestconfig.rootpath / 'docs' / 'configuration.rst'

    all_cfgs = []

    lines = []
    add = False
    indent = 0

    for line in file.read_text().splitlines():
        line = line
        stripped = line.strip()

        if add:
            if not indent and stripped:
                while line[indent] == ' ':
                    indent += 1

            if stripped and line[0] != ' ':
                all_cfgs.append(lines)
                add = False
                continue

            lines.append(line[indent:])

        if stripped.startswith('.. code-block:: yaml') or stripped.startswith('.. code-block:: yml'):
            add = True
            lines = []

    if add:
        all_cfgs.append(lines)

    for cfg_lines in all_cfgs:
        sample_cfg = '\n'.join(cfg_lines)

        map = yaml.yaml_rt.load(sample_cfg)
        CONFIG.load_config_dict(map)


def test_config_documentation_complete(pytestconfig):
    cfg_docs: Path = pytestconfig.rootpath / 'docs' / 'configuration.rst'
    cfg_model_dir: Path = pytestconfig.rootpath / 'src' / 'HABApp' / 'config' / 'models'
    assert cfg_model_dir.is_dir()

    documented_objs = set()

    # documented config
    current_module = ''
    for line in map(lambda x: x.strip().replace('  ', ''), cfg_docs.read_text().splitlines()):  # type: str
        if line.startswith('.. py:currentmodule::'):
            current_module = line[21:].strip()
            continue

        if line.startswith('.. autopydantic_model::'):
            obj_name = line[23:].strip()
            if current_module:
                obj_name = f'{current_module}.{obj_name}'
            assert obj_name not in documented_objs
            documented_objs.add(obj_name)

    # config implementation
    existing_objs = set()
    for module_name in [f.stem for f in cfg_model_dir.glob('**/*.py')]:
        module = getattr(HABApp.config.models, module_name)
        cfg_objs = [x[1] for x in getmembers(module, lambda x: isclass(x) and issubclass(x, BaseModel))]
        cfg_names = {
            f'{obj.__module__}.{obj.__qualname__}' for obj in cfg_objs if not obj.__module__.startswith('easyconfig.')
        }
        existing_objs.update(cfg_names)

        # we check this here to get the module with the error message
        missing = cfg_names - documented_objs
        assert not missing, module.__name__

    # ensure that everything that is implemented is documented
    assert existing_objs == documented_objs
