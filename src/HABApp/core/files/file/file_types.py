from __future__ import annotations

from pathlib import Path
from typing import Type, Dict

from HABApp.core.files.file import HABAppFile
from HABApp.core.files.file.properties import get_properties

FILE_TYPES: Dict[str, Type[HABAppFile]] = {}


def register_file_type(prefix: str, cls: Type[HABAppFile]):
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
    return cls(name, path, get_properties(txt))
