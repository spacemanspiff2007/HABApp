import re

from stack_data import LINE_GAP, FrameInfo

from HABApp.core.const.installation import HABAPP_MODULE_PATH, PYTHON_INSTALLATION_PATHS
from HABApp.core.lib.exceptions.const import PRE_INDENT, SEPARATOR_NEW_FRAME
from HABApp.core.lib.exceptions.format_frame_vars import format_frame_variables


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


def is_suppressed_habapp_file(name: str) -> bool:
    for r in SUPPRESSED_HABAPP_PATHS:
        if r.search(name):
            return True
    return False


def is_lib_file(name: str) -> bool:
    if name.startswith(HABAPP_MODULE_PATH):
        return False

    return bool(name.startswith(PYTHON_INSTALLATION_PATHS))


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
