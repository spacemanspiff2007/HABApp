import asyncio
import sys
import threading
from pathlib import Path
from typing import Final

import colorama
import pydantic


def __get_library_paths() -> tuple[str, ...]:
    found: set[str] = set()
    exec_folter = Path(sys.executable).parent
    found.add(str(exec_folter))

    # detect virtual environment
    if exec_folter.with_name('pyvenv.cfg').is_file():
        folder_names = ('bin', 'include', 'lib', 'lib64', 'scripts')
        for p in exec_folter.parent.iterdir():
            if p.name.lower() in folder_names and p.is_dir():
                found.add(str(p))

    # threading and asyncio are sometimes in a system-wide directory,
    # Pydantic and colorama should always be in the venv
    for m in (threading, asyncio, pydantic, colorama):
        f = Path(m.__file__)
        # sometimes it's a package, sometimes a module
        if f.name == '__init__.py':
            f = f.parent
        found.add(str(f.parent))

    # check if we already have the parent path
    ret = []
    for p in sorted(found):
        for parent in found:
            if p != parent and p.startswith(parent):
                break
        else:
            ret.append(p)

    return tuple(ret)


def _get_habapp_module_path() -> str:
    this = Path(__file__)
    while this.name != 'HABApp' or not this.is_dir():
        this = this.parent
    return str(this)


PYTHON_INSTALLATION_PATHS: Final = __get_library_paths()
HABAPP_MODULE_PATH: Final = _get_habapp_module_path()

del __get_library_paths
del _get_habapp_module_path
