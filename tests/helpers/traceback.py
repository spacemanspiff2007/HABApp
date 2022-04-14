import re
from pathlib import Path


def process_traceback(traceback: str) -> str:

    # object ids
    traceback = re.sub(r' at 0x[0-9A-Fa-f]+', ' at 0x' + 'A' * 16, traceback)

    # File path
    for m in re.finditer(r'File\s+"([^"]+)"', traceback):
        fname = "/".join(Path(m.group(1)).parts[-3:])
        traceback = traceback.replace(m.group(0), f'File "{fname}"')

    return traceback
