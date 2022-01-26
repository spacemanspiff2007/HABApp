import logging
import re
import typing
from pathlib import Path

import stackprinter

log = logging.getLogger('HABApp')


SUPPRESSED_PATHS = (
    re.compile(f'[/\\\\]{Path(__file__).name}$'),   # this file

    # rule file loader
    re.compile(r'[/\\]rule_file.py$'),
    re.compile(r'[/\\]runpy.py$'),

    # Worker functions
    re.compile(r'[/\\]wrappedfunction.py$'),

    # Don't print stack for used libraries/python functions
    re.compile(r'[/\\](site-packages|lib|python\d\.\d+)[/\\]asyncio[/\\]'),
    re.compile(r'[/\\]site-packages[/\\](?!habapp)[^/\\]+[/\\]'),
)

SKIP_TB = tuple(re.compile(k.pattern.replace('$', ', ')) for k in SUPPRESSED_PATHS)


def format_exception(e: typing.Union[Exception, typing.Tuple[typing.Any, typing.Any, typing.Any]]) -> typing.List[str]:
    tb = []
    skip = 0

    lines = stackprinter.format(e, line_wrap=0, truncate_vals=2000, suppressed_paths=SUPPRESSED_PATHS).splitlines()
    for i, line in enumerate(lines):
        if not skip:
            for s in SKIP_TB:
                if s.search(line):
                    # if it's just a two line traceback we skip it
                    if lines[i + 1].startswith('    ') and lines[i + 2].startswith('File'):
                        skip = 2
                        continue
        if skip:
            skip -= 1
            continue

        tb.append(line)

    return tb
