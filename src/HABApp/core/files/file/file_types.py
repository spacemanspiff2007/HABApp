from __future__ import annotations

import logging
from pathlib import Path

from pydantic import ValidationError

from HABApp.core.files.file import HABAppFile, FileState
from HABApp.core.files.file.properties import get_properties, FileProperties
from HABApp.core.logger import HABAppError

FILE_TYPES: dict[str, type[HABAppFile]] = {}


log = logging.getLogger('HABApp.files')


def register_file_type(prefix: str, cls: type[HABAppFile]):
    assert prefix not in FILE_TYPES

    assert cls.LOGGER
    assert cls.LOAD_FUNC
    assert cls.UNLOAD_FUNC

    FILE_TYPES[prefix] = cls


def create_file(name: str, path: Path) -> HABAppFile:
    for prefix, cls in FILE_TYPES.items():
        if name.startswith(prefix):
            break
    else:
        raise ValueError(f'Unknown file type for "{name}"!')

    with path.open('r', encoding='utf-8') as f:
        txt = f.read(10 * 1024)

    validation_error = True

    try:
        properties = get_properties(txt)
        validation_error = False
    except ValidationError as e:
        logger = HABAppError(log)
        logger.add(f'Error while parsing properties for {name:s}:')
        for line in str(e).splitlines()[1:]:
            logger.add(f'  {line:s}')
        logger.dump()

        properties = FileProperties()

    obj = cls(name, path, properties)
    if validation_error:
        obj.set_state(FileState.PROPERTIES_INVALID)

    return obj
