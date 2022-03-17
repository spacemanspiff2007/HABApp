import re
from pathlib import Path

import HABApp.__check_dependency_packages__


def test_installation_check():
    re_name = re.compile(r'^([A-Za-z-]{3,})')
    requirements = Path(__file__).parent.parent / 'requirements_setup.txt'
    assert requirements.is_file()

    found = set()
    for line in requirements.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        found.add(re_name.search(line).group(1))

    # Only backwards compatibility
    found.remove('typing-extensions')

    coded = set(HABApp.__check_dependency_packages__.get_dependencies())

    assert coded == found
