import logging
from pathlib import Path

import pytest
from easyconfig import create_app_config
from pydantic import BaseModel

import HABApp
from HABApp.core.const.const import PYTHON_311, PYTHON_312, PYTHON_313
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


def func_obj_def_multilines() -> None:
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


def func_test_assert_none(a: str | None = None, b: str | None = None, c: str | int = 3) -> None:
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


@pytest.mark.skipif(PYTHON_311 or PYTHON_312 or PYTHON_313, reason='Traceback Python 3.10')
def test_exception_expression_remove_py310() -> None:
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
     91 | def func_test_assert_none(a: str | None = None, b: str | None = None, c: str | int = 3) -> None:
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


@pytest.mark.skipif(PYTHON_313, reason='New traceback from python 3.11 and 3.12')
def test_exception_expression_remove_py_311_312() -> None:
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
     91 | def func_test_assert_none(a: str | None = None, b: str | None = None, c: str | int = 3) -> None:
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


@pytest.mark.skipif(not PYTHON_313, reason='New traceback from python 3.13')
def test_exception_expression_remove() -> None:
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
     91 | def func_test_assert_none(a: str | None = None, b: str | None = None, c: str | int = 3) -> None:
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
     ~~~~^^
  File "test_core/test_lib/test_format_traceback.py", line 97, in func_test_assert_none
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero'''


def func_ir() -> None:

    from HABApp.core.items import Item
    Items = HABApp.core.Items

    Items.add_item(Item('asdf'))
    Items.get_item('1234')


@pytest.fixture
def _setup_ir(clean_objs, monkeypatch, ir, eb):

    from HABApp.core.internals.proxy import ConstProxyObj
    assert isinstance(HABApp.core.Items, ConstProxyObj)
    assert isinstance(HABApp.core.EventBus, ConstProxyObj)

    monkeypatch.setattr(HABApp.core, 'Items', ir)
    monkeypatch.setattr(HABApp.core, 'EventBus', eb)

    yield


@pytest.mark.skipif(not PYTHON_313, reason='New traceback from python 3.13')
def test_skip_objs(_setup_ir) -> None:
    log.setLevel(logging.WARNING)
    msg = exec_func(func_ir)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line 21 in exec_func
--------------------------------------------------------------------------------
     19 | def exec_func(func) -> str:
     20 |     try:
-->  21 |         func()
     22 |     except Exception as e:
   ------------------------------------------------------------
     e = ItemNotFoundException('Item 1234 does not exist!')
     func = <function func_ir at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line 253 in func_ir
--------------------------------------------------------------------------------
     199 | def func_ir() -> None:
     201 |     from HABApp.core.items import Item
     202 |     Items = HABApp.core.Items
     204 |     Items.add_item(Item('asdf'))
-->  205 |     Items.get_item('1234')

File "internals/item_registry/item_registry.py", line 31 in get_item
--------------------------------------------------------------------------------
     27 | def get_item(self, name: str) -> ItemRegistryItem:
     28 |     try:
     29 |         return self._items[name]
     30 |     except KeyError:
-->  31 |         raise ItemNotFoundException(name) from None
   ------------------------------------------------------------
     name = '1234'
   ------------------------------------------------------------

--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "test_core/test_lib/test_format_traceback.py", line 21, in exec_func
    func()
     ~~~~^^
  File "test_core/test_lib/test_format_traceback.py", line 205, in func_ir
    Items.get_item('1234')
     ~~~~~~~~~~~~~~^^^^^^^^
  File "internals/item_registry/item_registry.py", line 31, in get_item
    raise ItemNotFoundException(name) from None
HABApp.core.errors.ItemNotFoundException: Item 1234 does not exist!'''


def test_habapp_regex(pytestconfig):

    files = tuple(str(f) for f in (Path(pytestconfig.rootpath) / 'src' / 'HABApp').glob('**/*'))

    for regex in SUPPRESSED_HABAPP_PATHS:
        for file in files:
            if regex.search(file):
                break
        else:
            msg = f'Nothing matched for {regex}'
            raise ValueError(msg)


def test_regex(pytestconfig) -> None:  # noqa: ARG001

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
