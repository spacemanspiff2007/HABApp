from io import StringIO
from pathlib import Path, PurePath
from typing import Any, Callable, TextIO, Union
from warnings import warn


class MyStringIO(StringIO):

    def __init__(self, close_cb: Callable[[str], Any], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.close_cb = close_cb

    def close(self) -> None:
        self.close_cb(self.getvalue())
        super().close()


class MockFile:

    def __init__(self, path: str, data: str = ''):
        super().__init__()

        self.path = Path(path)
        self.data: str = data
        self.warn_on_delete = True

    def __set_data(self, val: str):
        self.data = val

    def is_file(self) -> bool:
        return True

    def open(self, *args, **kwargs) -> TextIO:
        return MyStringIO(self.__set_data, self.data)

    def rename(self, target: Union[str, PurePath]):
        if self.warn_on_delete:
            warn(f'Not supported for {self.__class__.__name__}!', UserWarning, stacklevel=2)
        return None

    def replace(self, target: Union[str, PurePath]) -> None:
        if self.warn_on_delete:
            warn(f'Not supported for {self.__class__.__name__}!', UserWarning, stacklevel=2)
        return None

    def rmdir(self) -> None:
        if self.warn_on_delete:
            warn(f'Not supported for {self.__class__.__name__}!', UserWarning, stacklevel=2)
        return None

    def unlink(self) -> None:
        if self.warn_on_delete:
            warn(f'Not supported for {self.__class__.__name__}!', UserWarning, stacklevel=2)
        return None

    # -----------------------------------------------------------------------------------
    # Funcs that are just passed through
    def with_suffix(self, suffix):
        c = self.__class__(self.path.with_suffix(suffix))
        c.warn_on_delete = self.warn_on_delete
        return c

    @property
    def name(self):
        return self.path.name

    def read_text(self, encoding: str) -> str:
        return self.data
