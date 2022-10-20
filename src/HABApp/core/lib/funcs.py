from pathlib import Path
from typing import List, Iterable, TYPE_CHECKING
import operator as _operator

from HABApp.core.const import MISSING

if TYPE_CHECKING:
    import HABApp


def list_files(folder: Path, file_filter: 'HABApp.core.files.watcher.file_watcher.EventFilterBase',
               recursive: bool = False) -> List[Path]:
    # glob is much quicker than iter_dir()
    files = folder.glob('**/*' if recursive else '*')
    return sorted(filter(lambda x: file_filter.notify(str(x)), files), key=lambda x: x.relative_to(folder))


def sort_files(files: Iterable[Path]) -> List[Path]:
    return sorted(files)


CMP_OPS = {
    'lt': _operator.lt, 'lower_than': _operator.lt,
    'le': _operator.le, 'lower_equal': _operator.le,
    'eq': _operator.eq, 'equal': _operator.eq,
    'ne': _operator.ne, 'not_equal': _operator.ne,
    'gt': _operator.gt, 'greater_than': _operator.gt,
    'ge': _operator.ge, 'greater_equal': _operator.ge,

    'is_': _operator.is_,
    'is_not': _operator.is_not,
}


def compare(value, **kwargs) -> bool:

    for name, cmp_value in kwargs.items():
        if cmp_value is MISSING:
            continue
        if CMP_OPS[name](value, cmp_value):
            return True
    return False
