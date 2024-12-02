import re
import sys
from pathlib import Path
from typing import Final

from stack_data import LINE_GAP, FrameInfo

from .const import PRE_INDENT, SEPARATOR_NEW_FRAME
from .format_frame_vars import format_frame_variables


SUPPRESSED_HABAPP_PATHS = (
    # This exception formatter
    re.compile(r'[/\\]HABApp[/\\]core[/\\]lib[/\\]exceptions[/\\]'),
    # Wrapper which usually generates this traceback
    re.compile(r'[/\\]HABApp[/\\]core[/\\]wrapper.py'),

    # Rule file loader
    re.compile(r'[/\\]HABApp[/\\]rule_manager[/\\]'),

    # Worker functions
    re.compile(r'[/\\]HABApp[/\\]core[/\\]internals[/\\]wrapped_function[/\\]'),

    # Item registry
    re.compile(r'[/\\]HABApp[/\\]core[/\\]internals[/\\]item_registry[/\\]'),

    # Connection wrappers
    re.compile(r'[/\\]HABApp[/\\]core[/\\]connections[/\\]'),
)


def __get_library_paths() -> tuple[str, ...]:
    ret = []
    exec_folter = Path(sys.executable).parent
    ret.append(str(exec_folter))

    # detect virtual environment
    if exec_folter.with_name('pyvenv.cfg').is_file():
        folder_names = ('bin', 'include', 'lib', 'lib64', 'scripts')
        for p in exec_folter.parent.iterdir():
            if p.name.lower() in folder_names and (value := str(p)) not in ret and p.is_dir():
                ret.append(value)

    return tuple(ret)


def _get_habapp_module_path() -> str:
    this = Path(__file__)
    while this.name != 'HABApp' or not this.is_dir():
        this = this.parent
    return str(this)


SUPPRESSED_PATHS: Final = __get_library_paths()
HABAPP_MODULE_PATH: Final = _get_habapp_module_path()
del __get_library_paths
del _get_habapp_module_path


def is_suppressed_habapp_file(name: str) -> bool:
    for r in SUPPRESSED_HABAPP_PATHS:
        if r.search(name):
            return True
    return False


def is_lib_file(name: str) -> bool:
    if name.startswith(HABAPP_MODULE_PATH):
        return False

    return bool(name.startswith(SUPPRESSED_PATHS))



def format_frame_info(tb: list[str], frame_info: FrameInfo, is_last=False) -> bool:
    filename = frame_info.filename

    # always skip system and python libraries
    if is_lib_file(filename):
        return False

    if not is_last and is_suppressed_habapp_file(filename):
        return False

    # calc max line nr for indentation
    max_line = frame_info.lineno + frame_info.options.after
    # it's possible that his list is empty (e.g. if we execode in sphinx-exec-code)
    if frame_info.lines:
        max_line = frame_info.lines[-1].lineno

    indent = len(str(max_line)) + 1

    tb.append(f'File "{filename}", line {frame_info.lineno} in {frame_info.code.co_name}')
    tb.append(SEPARATOR_NEW_FRAME)
    for line in frame_info.lines:
        if line is LINE_GAP:
            tb.append(f"{' ' * (PRE_INDENT + indent - 1)}(...)")
        else:
            tb.append(f"{'-->' if line.is_current else '':{PRE_INDENT}s}{line.lineno:{indent}d} | {line.render()}")

    format_frame_variables(tb, frame_info.variables)
    tb.append('')
    return True
