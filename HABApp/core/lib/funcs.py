from pathlib import Path
from typing import List, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    import HABApp


def list_files(folder: Path, file_filter: 'HABApp.core.files.watcher.file_watcher.EventFilterBase',
               recursive: bool = False) -> List[Path]:
    # glob is much quicker than iter_dir()
    files = folder.glob('**/*' if recursive else '*')
    return sorted(filter(lambda x: file_filter.notify(str(x)), files), key=lambda x: x.relative_to(folder))


def sort_files(files: Iterable[Path]) -> List[Path]:
    return sorted(files)
