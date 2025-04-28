import re
from pathlib import Path
from typing import Final

from openhab_runner.const import log_placeholder as log
from openhab_runner.models import CONFIG


RE_PLACEHOLDER = re.compile(r'%([^%]+)%')


class ConfigPlaceholder:
    def __init__(self) -> None:
        self._placeholder: Final[dict[str, str]] = {}

    def add(self, name: str, value: str) -> str:
        if not isinstance(name, str):
            raise TypeError()
        if not isinstance(value, str):
            raise TypeError()

        if (existing := self._placeholder.get(name)) is not None and existing != value:
            msg = f'Key {name} already exists with value {existing}'
            raise ValueError(msg)

        self._placeholder[name] = value
        log.debug(f'{f"%{name:s}%":>20s}: {value:s}')
        return value

    def replace_env(self, value: str) -> str:
        if '%' not in value:
            return value

        # For env vars we can only replace existing values because
        # % is a valid env var character under windows
        for name, replacement in self._placeholder.items():
            value = value.replace(f'%{name:s}%', self._replace(replacement))
        return value

    def _replace(self, value: str, path: tuple[str, ...] = ()) -> str:
        if '%' not in value:
            return value

        while (m := RE_PLACEHOLDER.search(value)) is not None:
            key = m.group(1)
            if key in path:
                msg = f'Circular reference detected: {"->".join(path)}'
                raise ValueError(msg)
            value = value[:m.start()] + self._replace(self._placeholder[key], path + (key, )) + value[m.end():]

        return value

    def _get_path(self, value: str, *, add_as: str | None = None) -> Path:
        new_value = self._replace(value)

        p = Path(new_value)
        if not p.is_absolute():
            p = CONFIG.loaded_file_path.parent / p
        return p.resolve()

    def get_folder_path(self, value: str, *, must_exist: bool = True, add_as: str | None = None) -> Path:
        p = self._get_path(value, add_as=add_as)

        if must_exist and not p.is_dir():
            msg = f'{p} is not a directory!'
            raise FileNotFoundError(msg)

        if add_as is not None:
            self.add(add_as, p.as_posix())
        return p

    def get_file_path(self, value: str, *, must_exist: bool = True, add_as: str | None = None) -> Path:
        p = self._get_path(value, add_as=add_as)

        if must_exist and not p.is_file():
            msg = f'{p} is not a file!'
            raise FileNotFoundError(msg)

        if add_as is not None:
            self.add(add_as, p.as_posix())
        return p

    def __call__(self, value: str) -> str:
        return self._replace(value)
