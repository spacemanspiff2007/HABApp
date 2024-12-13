import re

from pydantic import BaseModel, ConfigDict, Field

from HABApp.core.const import yml


class FileProperties(BaseModel):
    depends_on: list[str] = Field(alias='depends on', default_factory=list)
    reloads_on: list[str] = Field(alias='reloads on', default_factory=list)

    model_config = ConfigDict(extra='forbid', populate_by_name=True)


RE_START = re.compile(r'^(\s*#\s*)HABApp\s*:', re.IGNORECASE)


def get_file_properties(_str: str) -> FileProperties:

    cfg = []
    cut = 0

    # extract the property string
    for line in _str.splitlines():
        line_strip = line.strip()
        if cut and not line_strip:
            break

        if not line_strip:
            continue

        # break on first non-empty line that is not a comment
        if line_strip and not line_strip.startswith('#'):
            break

        if not cut:
            # find out how much from the start we have to cut
            if m := RE_START.search(line):
                cut = m.end(1)
                cfg.append(line[cut:].lower())
        else:
            # If we would cut away characters it's not the yaml definition any more
            # Here it's cut + 1 because it must be indented
            if line[:cut + 1].strip() not in ('', '#'):
                break
            cfg.append(line[cut:])

    data = yml.load('\n'.join(cfg))
    if data is None:
        data = {}
    return FileProperties.model_validate(data.get('habapp', {}))
