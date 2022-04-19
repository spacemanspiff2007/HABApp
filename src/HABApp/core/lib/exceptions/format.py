from traceback import format_exception as _format_exception
from typing import Tuple, Union, Any, List

from stack_data import FrameInfo, Options

from .const import SEPARATOR_NEW_FRAME
from .format_frame import format_frame_info


def append_short_traceback(tb: List[str], e: Union[Exception, Tuple[Any, Any, Any]]):
    for line in _format_exception(*e) if isinstance(e, tuple) else _format_exception(type(e), e, e.__traceback__):
        for sub_lines in line.splitlines():
            tb.append(sub_lines.rstrip())


DEFAULT_OPTIONS = Options(include_signature=True, max_lines_per_piece=5)


def format_exception(e: Union[Exception, Tuple[Any, Any, Any]]) -> List[str]:
    tb = []

    try:
        all_frames = tuple(FrameInfo.stack_data(e[2] if isinstance(e, tuple) else e.__traceback__, DEFAULT_OPTIONS))
        last_frame = len(all_frames) - 1

        added = True
        for i, frame_info in enumerate(all_frames):
            if isinstance(frame_info, FrameInfo):
                added = format_frame_info(tb, frame_info, is_last=i == last_frame)
            else:
                # repeated frames in case of recursion
                if added:
                    tb.append(f"... {frame_info.description} ...\n")

        # add a short traceback
        tb.append(SEPARATOR_NEW_FRAME)
        append_short_traceback(tb, e)

    except Exception as e:
        # in case something goes wrong while formatting the traceback
        # we still want to show at least a small error message!
        new_tb = [f'Error while formatting traceback: {e}']
        append_short_traceback(new_tb, e)

        # add traceback so we have some more information
        new_tb.append('')
        new_tb.append(SEPARATOR_NEW_FRAME)
        new_tb.append('Partial Traceback:')
        new_tb.append(SEPARATOR_NEW_FRAME)
        new_tb.append('')
        new_tb.extend(tb)
        return new_tb

    return tb