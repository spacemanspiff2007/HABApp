from easyconfig import yaml
from HABApp.config import CONFIG


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
