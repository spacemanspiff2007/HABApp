import re
from pathlib import Path


def remove_dyn_parts_from_traceback(traceback: str) -> str:

    # object ids
    traceback = re.sub(r' at 0x[0-9A-Fa-f]+', ' at 0x' + 'A' * 16, traceback)

    # File path
    for m in re.finditer(r'File\s+"([^"]+)"', traceback):
        fname = '/'.join(Path(m.group(1)).parts[-3:])
        traceback = traceback.replace(m.group(0), f'File "{fname}"')

    # Line nrs
    traceback = re.sub(r'line\s+(\d+)', 'line x', traceback)
    traceback = re.sub(r'^(-->|\s{3})\s{2}\d+ \|', '\g<1>  x |', traceback, flags=re.MULTILINE)

    return traceback


def test_remove_dyn_parts_from_traceback() -> None:

    traceback = '''
File "C:\\My\\Folder\\HABApp\\tests\\test_core\\test_lib\\test_format_traceback.py", line 19 in exec_func
File "/My/Folder/HABApp/tests/test_core/test_lib/test_format_traceback.py", line 19 in exec_func
func = <function func_test_assert_none at 0x0000022A46E3C550>
  File "C:\\My\\Folder\\HABApp\\tests\\test_core\\test_lib\\test_format_traceback.py", line 19, in exec_func
     16 |     try:
-->  17 |         func()
     18 |     except Exception as e:
'''
    processed = remove_dyn_parts_from_traceback(traceback)

    assert processed == '''
File "test_core/test_lib/test_format_traceback.py", line x in exec_func
File "test_core/test_lib/test_format_traceback.py", line x in exec_func
func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
  File "test_core/test_lib/test_format_traceback.py", line x, in exec_func
     x |     try:
-->  x |         func()
     x |     except Exception as e:
'''
