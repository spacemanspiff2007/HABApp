import re
from pathlib import Path


def remove_dyn_parts_from_traceback(traceback: str) -> str:

    # object ids
    traceback = re.sub(r' at 0x[0-9A-Fa-f]+', ' at 0x' + 'A' * 16, traceback)

    # File path
    for m in re.finditer(r'File\s+"([^"]+)"', traceback):
        fname = "/".join(Path(m.group(1)).parts[-3:])
        traceback = traceback.replace(m.group(0), f'File "{fname}"')

    return traceback


def test_remove_dyn_parts_from_traceback():

    traceback = """
File "C:\\My\\Folder\\HABApp\\tests\\test_core\\test_lib\\test_format_traceback.py", line 19 in exec_func
File "/My/Folder/HABApp/tests/test_core/test_lib/test_format_traceback.py", line 19 in exec_func
func = <function func_test_assert_none at 0x0000022A46E3C550>
  File "C:\\My\\Folder\\HABApp\\tests\\test_core\\test_lib\\test_format_traceback.py", line 19, in exec_func
"""
    processed = remove_dyn_parts_from_traceback(traceback)

    assert processed == """
File "test_core/test_lib/test_format_traceback.py", line 19 in exec_func
File "test_core/test_lib/test_format_traceback.py", line 19 in exec_func
func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
  File "test_core/test_lib/test_format_traceback.py", line 19, in exec_func
"""
