import re
from typing import List

from stack_data import FrameInfo, LINE_GAP

from .const import SEPARATOR_NEW_FRAME, PRE_INDENT
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
)

SUPPRESSED_PATHS = (
    # Libraries of base installation
    re.compile(r'[/\\](?:python\d\.\d+|python\d{2,3})[/\\]lib[/\\]', re.IGNORECASE),
    # Libraries in venv
    re.compile(r'[/\\]lib[/\\]site-packages[/\\]', re.IGNORECASE),
)


def skip_file(name: str) -> bool:
    for r in (SUPPRESSED_HABAPP_PATHS if '/HABApp/' in name or '\\HABApp\\' in name else SUPPRESSED_PATHS):
        if r.search(name):
            return True
    return False


def format_frame_info(tb: List[str], frame_info: FrameInfo, is_last=False) -> bool:
    filename = frame_info.filename

    if not is_last and skip_file(filename):
        return False

    # get indentation based on max lineno
    max_line = frame_info.lines[-1].lineno
    indent = 1
    while 10 ** indent < max_line:
        indent += 1
    indent += 1

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
