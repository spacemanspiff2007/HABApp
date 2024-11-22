from pathlib import Path


def _get_file_name(file: Path, nr: int) -> Path:
    if nr < 0:
        raise ValueError()

    if nr:
        return file.with_name(f'{file.name:s}.{nr:d}')
    return file


def rotate_file(file: Path, backup_count: int) -> None:
    if not isinstance(backup_count, int):
        raise TypeError()

    _get_file_name(file, backup_count).unlink(missing_ok=True)
    for i in range(backup_count - 1, -1, -1):
        src = _get_file_name(file, i)
        if not src.is_file():
            continue

        dst = _get_file_name(file, i + 1)
        dst.unlink(missing_ok=True)
        src.rename(dst)
