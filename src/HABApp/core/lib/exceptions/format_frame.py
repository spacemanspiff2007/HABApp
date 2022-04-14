import re
from pathlib import Path
from typing import List

from stack_data import FrameInfo, LINE_GAP

from .const import SEPARATOR_NEW_FRAME, PRE_INDENT
from .format_frame_vars import format_frame_variables

SUPPRESSED_PATHS = (
    re.compile(f'[/\\\\]{Path(__file__).name}$'),   # this file

    # rule file loader
    re.compile(r'[/\\]rule_file.py$'),
    re.compile(r'[/\\]runpy.py$'),

    # Worker functions
    re.compile(r'[/\\]wrappedfunction.py$'),

    # Don't print stack traces for used libraries/python functions except for HABApp
    re.compile(r'[/\\](site-packages|lib|python\d\.\d+)[/\\](?!habapp)[^/\\]+[/\\]'),
)


def skip_file(name: str) -> bool:
    for r in SUPPRESSED_PATHS:
        if r.search(name):
            return True
    return False


def format_frame_info(tb: List[str], frame_info: FrameInfo) -> bool:
    filename = frame_info.filename

    if skip_file(filename):
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
