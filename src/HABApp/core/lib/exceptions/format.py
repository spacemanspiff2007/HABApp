from traceback import format_exception as _format_exception
from types import TracebackType
from typing import Tuple, Union, Any, List, Type

from HABApp.core.const.const import PYTHON_310

if PYTHON_310:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


from stack_data import FrameInfo, Options

from .const import SEPARATOR_NEW_FRAME
from .format_frame import format_frame_info


def append_short_traceback(tb: List[str], e: Union[Exception, Tuple[Any, Any, Any]]):
    for line in _format_exception(*e) if isinstance(e, tuple) else _format_exception(type(e), e, e.__traceback__):
        for sub_lines in line.splitlines():
            tb.append(sub_lines.rstrip())


DEFAULT_OPTIONS = Options(include_signature=True, max_lines_per_piece=5)


def fallback_format(e: Exception, existing_traceback: List[str]) -> List[str]:
    # in case something goes wrong while formatting the traceback
    # we still want to show at least a small error message!
    new_tb = [f'Error while formatting traceback: {e}']
    append_short_traceback(new_tb, e)
    print(new_tb)

    # add traceback so we have some more information
    if existing_traceback:
        new_tb.append('')
        new_tb.append(SEPARATOR_NEW_FRAME)
        new_tb.append('Partial Traceback:')
        new_tb.append(SEPARATOR_NEW_FRAME)
        new_tb.extend(existing_traceback)
    return new_tb


HINT_EXCEPTION: TypeAlias = Union[Exception, Tuple[Type[Exception], Exception, TracebackType]]


def format_exception(e: HINT_EXCEPTION) -> List[str]:
    tb: List[str] = []

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
        return fallback_format(e, tb)

    return tb
