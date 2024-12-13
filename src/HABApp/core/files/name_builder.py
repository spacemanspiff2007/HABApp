from collections.abc import Generator, Iterable
from pathlib import Path
from re import Pattern
from typing import Final


class FileNameBuilderRule:
    def __init__(self, prefix: str, folder: str, *,
                 priority: int, pattern: Pattern | None = None) -> None:
        self.prefix: Final = prefix
        self.folder: Final = folder
        self.priority: Final = priority
        self.pattern: Final = pattern

    def create_name(self, path: str) -> str | None:
        if not path.startswith(folder := self.folder):
            return None

        if (p := self.pattern) is not None and not p.search(path):
            return None
        return self.prefix + path.removeprefix(folder)

    def create_path(self, name: str) -> Path | None:
        if not name.startswith(prefix := self.prefix):
            return None

        if (p := self.pattern) is not None and not p.search(name):
            return None

        return Path(self.folder + name.removeprefix(prefix))

    def matches_name(self, name: str) -> bool:
        return name.startswith(self.prefix) and (self.pattern is None or self.pattern.search(name))


class FileNameBuilder:
    def __init__(self) -> None:
        self._builders: tuple[FileNameBuilderRule, ...] = ()

    def add_folder(self, prefix: str, folder: Path, *,
                   priority: int, pattern: Pattern | None = None) -> None:
        for b in self._builders:
            if b.priority == priority:
                msg = f'Priority {priority} already exists for {b.prefix}!'
                raise ValueError(msg)

        new = FileNameBuilderRule(prefix, folder.as_posix() + '/', priority=priority, pattern=pattern)
        self._builders = tuple(sorted(self._builders + (new,), key=lambda x: x.priority, reverse=True))

    def create_name(self, path: str) -> str:
        paths = [n for b in self._builders if (n := b.create_name(path)) is not None]
        if not paths:
            msg = f'Nothing matched for path {path:s}'
            raise ValueError(msg)

        if len(paths) > 1:
            msg = f'Multiple matches for path {path:s}: {", ".join(paths)}'
            raise ValueError(msg)

        return paths[0]

    def create_path(self, name: str) -> Path:
        paths = [p for b in self._builders if (p := b.create_path(name)) is not None]
        if not paths:
            msg = f'Nothing matched for name {name:s}'
            raise ValueError(msg)

        if len(paths) > 1:
            msg = f'Multiple matches for name {name:s}: {", ".join(p.as_posix() for p in paths)}'
            raise ValueError(msg)

        return paths[0]

    def is_accepted_path(self, path: str) -> bool:
        return any(b.create_name(path) is not None for b in self._builders)

    def is_accepted_name(self, path: str) -> bool:
        return any(b.matches_name(path) for b in self._builders)

    def get_folders(self) -> list[str]:
        ret: list[str] = []
        for b in self._builders:
            if b.folder not in ret:
                ret.append(b.folder)
        return ret

    def get_names_with_path(self, paths: list[str]) -> list[tuple[str, Path]]:
        ret = []
        for b in self._builders:
            ret.extend((n, Path(p)) for p in paths if (n := b.create_name(p)) is not None)
        return ret

    def get_names(self, names: Iterable[str]) -> Generator[str, None, None]:
        """Get sorted names"""
        names = sorted(names)
        for b in self._builders:
            for name in names:
                if b.matches_name(name):
                    yield name
