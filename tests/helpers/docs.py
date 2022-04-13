import re
from typing import Dict

regex = re.compile(r':ivar\s+(.+?)\s+(\w+):')


def get_ivars(obj) -> Dict[str, str]:
    ivars = {}
    for line in obj.__doc__.splitlines():
        if m := regex.search(line):
            name = m.group(2)
            type = m.group(1)
            assert name
            assert type
            assert name not in ivars
            ivars[name] = type
    return ivars
