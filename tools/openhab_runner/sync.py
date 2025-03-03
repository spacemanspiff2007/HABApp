import logging
from collections.abc import Iterable
from pathlib import Path
from shutil import rmtree

from openhab_runner.models import RunFolderSyncConfig, SyncOptionEnum


log = logging.getLogger('files')


def remove(obj: Path, *, mode: SyncOptionEnum, test: bool) -> None:

    if obj.is_dir():
        if mode == SyncOptionEnum.REMOVE_FILES_AND_FOLDERS:
            if test:
                log.info(f'Would remove {obj}')
                return None

            log.info(f'Removing {obj}')
            rmtree(obj)
            return None
        return None

    if test:
        log.info(f'Would remove {obj}')
        return None

    log.info(f'Removing {obj}')
    obj.unlink()
    return None


def copy_file(src: Path, dst: Path, test: bool) -> bool:
    src_bytes = src.read_bytes()

    if dst.is_file() and src_bytes == dst.read_bytes():
        return False

    if test:
        log.info(f'Would copy {src} to {dst}')
        return True

    log.info(f'Copy {src} to {dst}')
    dst.write_bytes(src_bytes)
    return True


def sync_folder(src_dir: Path, dst_dir: Path, *, mode: SyncOptionEnum, test: bool) -> int:
    copied = 0

    src_files: list[Path] = sorted(src_dir.iterdir())

    if mode != SyncOptionEnum.MERGE:
        dst_files: set[Path] = set(dst_dir.iterdir())
        dst_allowed = {dst_dir / src.name for src in src_files}

        if to_rem := (dst_files - dst_allowed):
            for obj in to_rem:
                remove(obj, mode=mode, test=test)

    for src_obj in src_files:
        dst_obj = dst_dir / src_obj.name

        if src_obj.is_file():
            copied += copy_file(src_obj, dst_obj, test=test)
            continue

        if not dst_obj.is_dir():
            if test:
                log.info(f'Would create directory {dst_obj}')
            else:
                log.info(f'Creating directory {dst_obj}')
                dst_obj.mkdir()

            copied += sync_folder(src_obj, dst_obj, mode=mode, test=test)
            continue

    return copied


def sync_data(objs: Iterable[RunFolderSyncConfig], *, test: bool) -> None:
    for obj in objs:
        copied = sync_folder(obj.src, obj.dst, mode=obj.mode, test=test)
        log.debug(f'Copied {copied} file{"s" if copied != 1 else ""} from {obj.src} to {obj.dst}')

    return None
