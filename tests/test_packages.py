import re
from pathlib import Path

from packaging.version import VERSION_PATTERN

import HABApp.__check_dependency_packages__
from HABApp import __version__
from HABApp.core.const.const import PYTHON_311


def test_installation_check() -> None:
    re_name = re.compile(r'^([A-Za-z_-]{3,})')
    requirements = Path(__file__).parent.parent / 'requirements_setup.txt'
    assert requirements.is_file()

    found = set()
    for line in requirements.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        found.add(re_name.search(line).group(1))

    if PYTHON_311:
        found.remove('taskgroup')

    coded = set(HABApp.__check_dependency_packages__.get_dependencies())

    assert coded == found


def test_version() -> None:
    check = re.compile(VERSION_PATTERN, re.VERBOSE | re.IGNORECASE)
    assert check.fullmatch(__version__)
