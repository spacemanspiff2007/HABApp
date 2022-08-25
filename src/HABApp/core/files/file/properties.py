import re
from typing import List

from pydantic import BaseModel, Extra, Field

from HABApp.core.const import yml


class FileProperties(BaseModel):
    depends_on: List[str] = Field(alias='depends on', default_factory=list)
    reloads_on: List[str] = Field(alias='reloads on', default_factory=list)

    class Config:
        extra = Extra.forbid
        allow_population_by_field_name = True


RE_START = re.compile(r'^#(\s*)HABApp\s*:', re.IGNORECASE)


def get_properties(_str: str) -> FileProperties:

    cfg = []
    cut = 0

    # extract the property string
    for line in _str.splitlines():
        line = line.strip()
        if cut and not line:
            break

        if not line:
            continue

        # break on first non-empty line that is not a comment
        if line and not line.startswith('#'):
            break

        if not cut:
            # find out how much from the start we have to cut
            m = RE_START.search(line)
            if m:
                cut = len(m.group(1)) + 1
                cfg.append(line[cut:].lower())
        else:
            do_break = False
            for i, c in enumerate(line):
                if i > cut:
                    break

                if c not in ('#', ' ', '\t'):
                    do_break = True
                    break
            if do_break:
                break

            cfg.append(line[cut:])

    data = yml.load('\n'.join(cfg))
    if data is None:
        data = {}
    return FileProperties.parse_obj(data.get('habapp', {}))
