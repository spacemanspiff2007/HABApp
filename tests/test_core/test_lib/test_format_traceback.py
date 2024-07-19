import logging
from pathlib import Path
from typing import Optional, Union

import pytest
from easyconfig import create_app_config
from pydantic import BaseModel

import HABApp
from HABApp.core.const.const import PYTHON_311
from HABApp.core.const.json import dump_json, load_json
from HABApp.core.lib import format_exception
from HABApp.core.lib.exceptions.format_frame import SUPPRESSED_HABAPP_PATHS, is_lib_file, is_suppressed_habapp_file
from tests.helpers.traceback import remove_dyn_parts_from_traceback


log = logging.getLogger('TestLogger')


def exec_func(func) -> str:
    try:
        func()
    except Exception as e:
        msg = '\n' + '\n'.join(format_exception(e))

    msg = remove_dyn_parts_from_traceback(msg)
    return msg


def func_obj_def_multilines():
    item = HABApp.core.items.Item
    a = [
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
#      26 |     item = HABApp.core.items.Item
#      27 |     a = [
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


@pytest.mark.skipif(PYTHON_311, reason='Traceback Python 3.10')
def test_exception_expression_remove_py310():
    log.setLevel(logging.WARNING)
    msg = exec_func(func_test_assert_none)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line 21 in exec_func
--------------------------------------------------------------------------------
     19 | def exec_func(func) -> str:
     20 |     try:
-->  21 |         func()
     22 |     except Exception as e:
   ------------------------------------------------------------
     e = ZeroDivisionError('division by zero')
     func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line 97 in func_test_assert_none
--------------------------------------------------------------------------------
     91 | def func_test_assert_none(a: Optional[str] = None, b: Optional[str] = None, c: Union[str, int] = 3):
      (...)
     94 |     assert isinstance(c, (str, int)), type(c)
     95 |     CONFIGURATION = '3'
     96 |     my_dict = {'key_a': 'val_a'}
-->  97 |     1 / 0
     98 |     log.error('Error message')
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
  File "test_core/test_lib/test_format_traceback.py", line 21, in exec_func
    func()
  File "test_core/test_lib/test_format_traceback.py", line 97, in func_test_assert_none
    1 / 0
ZeroDivisionError: division by zero'''


@pytest.mark.skipif(not PYTHON_311, reason='New traceback from python 3.11')
def test_exception_expression_remove():
    log.setLevel(logging.WARNING)
    msg = exec_func(func_test_assert_none)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line 21 in exec_func
--------------------------------------------------------------------------------
     19 | def exec_func(func) -> str:
     20 |     try:
-->  21 |         func()
     22 |     except Exception as e:
   ------------------------------------------------------------
     e = ZeroDivisionError('division by zero')
     func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line 97 in func_test_assert_none
--------------------------------------------------------------------------------
     91 | def func_test_assert_none(a: Optional[str] = None, b: Optional[str] = None, c: Union[str, int] = 3):
      (...)
     94 |     assert isinstance(c, (str, int)), type(c)
     95 |     CONFIGURATION = '3'
     96 |     my_dict = {'key_a': 'val_a'}
-->  97 |     1 / 0
     98 |     log.error('Error message')
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
  File "test_core/test_lib/test_format_traceback.py", line 21, in exec_func
    func()
  File "test_core/test_lib/test_format_traceback.py", line 97, in func_test_assert_none
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero'''


def test_habapp_regex(pytestconfig):

    files = tuple(str(f) for f in (Path(pytestconfig.rootpath) / 'src' / 'HABApp').glob('**/*'))

    for regex in SUPPRESSED_HABAPP_PATHS:
        for file in files:
            if regex.search(file):
                break
        else:
            raise ValueError(f'Nothing matched for {regex}')


def test_regex(pytestconfig):

    assert not is_suppressed_habapp_file('/lib/habapp/asdf')
    assert not is_suppressed_habapp_file('/lib/HABApp/asdf')
    assert not is_suppressed_habapp_file('/HABApp/core/lib/asdf')
    assert not is_suppressed_habapp_file('/HABApp/core/lib/asdf/asdf')

    assert is_lib_file(r'\Python310\lib\runpy.py')
    assert is_lib_file(r'/usr/lib/python3.10/runpy.py')
    assert is_lib_file(r'/opt/habapp/lib/python3.8/site-packages/aiohttp/client.py')
    assert is_lib_file(r'\Python310\lib\asyncio\tasks.py')
    assert is_lib_file(r'\Python310\lib\subprocess.py')

    # Normal HABApp installation under linux
    assert not is_lib_file('/opt/habapp/lib/python3.9/site-packages/HABApp/openhab/connection_logic/file.py')
    assert not is_suppressed_habapp_file(
        '/opt/habapp/lib/python3.9/site-packages/HABApp/openhab/connection_logic/file.py')
