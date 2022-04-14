import logging
from typing import Optional, Union

import HABApp
from HABApp.core.const.json import load_json, dump_json
from HABApp.core.lib import format_exception
from tests.helpers.traceback import process_traceback

log = logging.getLogger('TestLogger')


def exec_func(func) -> str:
    try:
        func()
    except Exception as e:
        msg = '\n' + '\n'.join(format_exception(e))

    msg = process_traceback(msg)
    return msg


def func_obj_def_multilines():
    item = HABApp.core.items.Item  # noqa: F841
    a = [  # noqa: F841
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
    ]
    1 / 0


def test_exception_format_traceback_compact_lines():

    msg = exec_func(func_obj_def_multilines)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line 14 in exec_func
--------------------------------------------------------------------------------
     12 | def exec_func(func) -> str:
     13 |     try:
-->  14 |         func()
     15 |     except Exception as e:
   ------------------------------------------------------------
     e = ZeroDivisionError('division by zero')
     func = <function func_obj_def_multilines at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line 34 in func_obj_def_multilines
--------------------------------------------------------------------------------
     22 | def func_obj_def_multilines():
     23 |     item = HABApp.core.items.Item  # noqa: F841
     24 |     a = [  # noqa: F841
     25 |         1,
      (...)
     32 |         8
     33 |     ]
-->  34 |     1 / 0
   ------------------------------------------------------------
     item = <class 'HABApp.core.items.item.Item'>
     a = [1, 2, 3, 4, 5, 6, 7, 8]
   ------------------------------------------------------------

--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "test_core/test_lib/test_format_traceback.py", line 14, in exec_func
    func()
  File "test_core/test_lib/test_format_traceback.py", line 34, in func_obj_def_multilines
    1 / 0
ZeroDivisionError: division by zero'''


def func_test_assert_none(a: Optional[str] = None, b: Optional[str] = None, c: Union[str, int] = 3):
    assert isinstance(a, str) or a is None, type(a)
    assert isinstance(b, str) or b is None, type(b)
    assert isinstance(c, (str, int)), type(c)
    1 / 0
    log.error('Error message')
    dump_json(load_json('a'))


def test_exception_expression_remove():
    log.setLevel(logging.WARNING)
    msg = exec_func(func_test_assert_none)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line 14 in exec_func
--------------------------------------------------------------------------------
     12 | def exec_func(func) -> str:
     13 |     try:
-->  14 |         func()
     15 |     except Exception as e:
   ------------------------------------------------------------
     e = ZeroDivisionError('division by zero')
     func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line 80 in func_test_assert_none
--------------------------------------------------------------------------------
     76 | def func_test_assert_none(a: Optional[str] = None, b: Optional[str] = None, c: Union[str, int] = 3):
     77 |     assert isinstance(a, str) or a is None, type(a)
     78 |     assert isinstance(b, str) or b is None, type(b)
     79 |     assert isinstance(c, (str, int)), type(c)
-->  80 |     1 / 0
     81 |     log.error('Error message')
   ------------------------------------------------------------
     a = None
     b = None
     c = 3
     log = <Logger TestLogger (WARNING)>
   ------------------------------------------------------------

--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "test_core/test_lib/test_format_traceback.py", line 14, in exec_func
    func()
  File "test_core/test_lib/test_format_traceback.py", line 80, in func_test_assert_none
    1 / 0
ZeroDivisionError: division by zero'''
