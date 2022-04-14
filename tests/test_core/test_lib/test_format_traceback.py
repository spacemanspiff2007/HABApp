import logging
from typing import Optional, Union

from pydantic import BaseModel

import HABApp
from HABApp.core.const.json import load_json, dump_json
from HABApp.core.lib import format_exception
from easyconfig import create_app_config
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


# def test_exception_format_traceback_compact_lines():
#
#     msg = exec_func(func_obj_def_multilines)
#     assert msg == r'''
# File "test_core/test_lib/test_format_traceback.py", line 17 in exec_func
# --------------------------------------------------------------------------------
#      15 | def exec_func(func) -> str:
#      16 |     try:
# -->  17 |         func()
#      18 |     except Exception as e:
#    ------------------------------------------------------------
#      e = ZeroDivisionError('division by zero')
#      func = <function func_obj_def_multilines at 0xAAAAAAAAAAAAAAAA>
#    ------------------------------------------------------------
#
# File "test_core/test_lib/test_format_traceback.py", line 37 in func_obj_def_multilines
# --------------------------------------------------------------------------------
#      25 | def func_obj_def_multilines():
#      26 |     item = HABApp.core.items.Item  # noqa: F841
#      27 |     a = [  # noqa: F841
#      28 |         1,
#       (...)
#      35 |         8
#      36 |     ]
# -->  37 |     1 / 0
#    ------------------------------------------------------------
#      item = <class 'HABApp.core.items.item.Item'>
#      a = [1, 2, 3, 4, 5, 6, 7, 8]
#    ------------------------------------------------------------
#
# --------------------------------------------------------------------------------
# Traceback (most recent call last):
#   File "test_core/test_lib/test_format_traceback.py", line 17, in exec_func
#     func()
#   File "test_core/test_lib/test_format_traceback.py", line 37, in func_obj_def_multilines
#     1 / 0
# ZeroDivisionError: division by zero'''


class DummyModel(BaseModel):
    a: int = 3
    b: str = 'asdf'


CONFIG = create_app_config(DummyModel())


def func_test_assert_none(a: Optional[str] = None, b: Optional[str] = None, c: Union[str, int] = 3):
    assert isinstance(a, str) or a is None, type(a)
    assert isinstance(b, str) or b is None, type(b)
    assert isinstance(c, (str, int)), type(c)
    CONFIGURATION = '3'
    my_dict = {'key_a': 'val_a'}
    1 / 0
    log.error('Error message')
    dump_json(load_json('a'))
    if CONFIG.a > 2:
        print('test')
    print(my_dict['key_a'])
    print(CONFIGURATION)


def test_exception_expression_remove():
    log.setLevel(logging.WARNING)
    msg = exec_func(func_test_assert_none)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line 17 in exec_func
--------------------------------------------------------------------------------
     15 | def exec_func(func) -> str:
     16 |     try:
-->  17 |         func()
     18 |     except Exception as e:
   ------------------------------------------------------------
     e = ZeroDivisionError('division by zero')
     func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line 93 in func_test_assert_none
--------------------------------------------------------------------------------
     87 | def func_test_assert_none(a: Optional[str] = None, b: Optional[str] = None, c: Union[str, int] = 3):
      (...)
     90 |     assert isinstance(c, (str, int)), type(c)
     91 |     CONFIGURATION = '3'
     92 |     my_dict = {'key_a': 'val_a'}
-->  93 |     1 / 0
     94 |     log.error('Error message')
   ------------------------------------------------------------
     CONFIG.a = 3
     a = None
     b = None
     c = 3
     CONFIGURATION = '3'
     log = <Logger TestLogger (WARNING)>
     my_dict = {'key_a': 'val_a'}
     my_dict['key_a'] = 'val_a'
     CONFIG.a > 2 = True
   ------------------------------------------------------------

--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "test_core/test_lib/test_format_traceback.py", line 17, in exec_func
    func()
  File "test_core/test_lib/test_format_traceback.py", line 93, in func_test_assert_none
    1 / 0
ZeroDivisionError: division by zero'''
