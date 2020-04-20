import typing
from pathlib import Path


def list_files(folder: Path, file_ending: str = '', recursive: bool = False) -> typing.List[Path]:
    # glob is much quicker than iter_dir()
    files = folder.glob(f'**/*{file_ending}' if recursive else f'*{file_ending}')
    return sorted(files, key=lambda x: x.relative_to(folder))
