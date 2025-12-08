import logging
from pathlib import Path

import pytest
from easyconfig import create_app_config
from pydantic import BaseModel

import HABApp
from HABApp.core.const.const import PYTHON_312, PYTHON_313
from HABApp.core.const.json import dump_json, load_json
from HABApp.core.lib import format_exception
from HABApp.core.lib.exceptions.format_frame import SUPPRESSED_HABAPP_PATHS, is_suppressed_habapp_file
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


@pytest.mark.skipif(
    PYTHON_313 or (not PYTHON_312 and not PYTHON_313),
    reason='New traceback from python 3.11 and 3.12')
def test_exception_expression_remove_py_311_312() -> None:
    log.setLevel(logging.WARNING)
    msg = exec_func(func_test_assert_none)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line x in exec_func
--------------------------------------------------------------------------------
     x | def exec_func(func) -> str:
     x |     try:
-->  x |         func()
     x |     except Exception as e:
   ------------------------------------------------------------
     e = ZeroDivisionError('division by zero')
     func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line x in func_test_assert_none
--------------------------------------------------------------------------------
     x | def func_test_assert_none(a: str | None = None, b: str | None = None, c: str | int = 3) -> None:
      (...)
     x |     assert isinstance(c, (str, int)), type(c)
     x |     CONFIGURATION = '3'
     x |     my_dict = {'key_a': 'val_a'}
-->  x |     1 / 0
     x |     log.error('Error message')
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
  File "test_core/test_lib/test_format_traceback.py", line x, in exec_func
    func()
  File "test_core/test_lib/test_format_traceback.py", line x, in func_test_assert_none
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero'''


@pytest.mark.skipif(not PYTHON_313, reason='New traceback from python 3.13')
def test_exception_expression_remove() -> None:
    log.setLevel(logging.WARNING)
    msg = exec_func(func_test_assert_none)
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line x in exec_func
--------------------------------------------------------------------------------
     x | def exec_func(func) -> str:
     x |     try:
-->  x |         func()
     x |     except Exception as e:
   ------------------------------------------------------------
     e = ZeroDivisionError('division by zero')
     func = <function func_test_assert_none at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line x in func_test_assert_none
--------------------------------------------------------------------------------
     x | def func_test_assert_none(a: str | None = None, b: str | None = None, c: str | int = 3) -> None:
      (...)
     x |     assert isinstance(c, (str, int)), type(c)
     x |     CONFIGURATION = '3'
     x |     my_dict = {'key_a': 'val_a'}
-->  x |     1 / 0
     x |     log.error('Error message')
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
  File "test_core/test_lib/test_format_traceback.py", line x, in exec_func
    func()
    ~~~~^^
  File "test_core/test_lib/test_format_traceback.py", line x, in func_test_assert_none
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
File "test_core/test_lib/test_format_traceback.py", line x in exec_func
--------------------------------------------------------------------------------
     x | def exec_func(func) -> str:
     x |     try:
-->  x |         func()
     x |     except Exception as e:
   ------------------------------------------------------------
     e = ItemNotFoundException('Item 1234 does not exist!')
     func = <function func_ir at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line x in func_ir
--------------------------------------------------------------------------------
     x | def func_ir() -> None:
     x |     from HABApp.core.items import Item
     x |     Items = HABApp.core.Items
     x |     Items.add_item(Item('asdf'))
-->  x |     Items.get_item('1234')

File "internals/item_registry/item_registry.py", line x in get_item
--------------------------------------------------------------------------------
     x | def get_item(self, name: str) -> ItemRegistryItem:
     x |     try:
     x |         return self._items[name]
     x |     except KeyError:
-->  x |         raise ItemNotFoundException(name) from None
   ------------------------------------------------------------
     name = '1234'
   ------------------------------------------------------------

--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "test_core/test_lib/test_format_traceback.py", line x, in exec_func
    func()
    ~~~~^^
  File "test_core/test_lib/test_format_traceback.py", line x, in func_ir
    Items.get_item('1234')
    ~~~~~~~~~~~~~~^^^^^^^^
  File "internals/item_registry/item_registry.py", line x, in get_item
    raise ItemNotFoundException(name) from None
HABApp.core.errors.ItemNotFoundException: Item 1234 does not exist!'''


def multiline_obj_name() -> None:

    class MultilineRepr:
        def __repr__(self) -> str:
            return '<\nmulti\nline>'

    instance = MultilineRepr()

    a = []

    if not a == [
        1,
        2
    ]:
        raise ValueError()


@pytest.mark.skipif(not PYTHON_313, reason='New traceback from python 3.13')
def test_multiple_statements() -> None:
    log.setLevel(logging.WARNING)
    msg = exec_func(multiline_obj_name)
    print('\n\n-')
    print(msg)
    print('\n\n')
    assert msg == r'''
File "test_core/test_lib/test_format_traceback.py", line x in exec_func
--------------------------------------------------------------------------------
     x | def exec_func(func) -> str:
     x |     try:
-->  x |         func()
     x |     except Exception as e:
   ------------------------------------------------------------
     e = ValueError()
     func = <function multiline_obj_name at 0xAAAAAAAAAAAAAAAA>
   ------------------------------------------------------------

File "test_core/test_lib/test_format_traceback.py", line x in multiline_obj_name
--------------------------------------------------------------------------------
     x | def multiline_obj_name() -> None:
       (...)
     x |     instance = MultilineRepr()
     x |     a = []
     x |     if not a == [
     x |         1,
     x |         2
     x |     ]:
-->  x |         raise ValueError()
   ------------------------------------------------------------
     a = []
     instance = <
                multi
                line>
     not a == [
             1,
             2
         ] = True
     a == [
             1,
             2
         ] = False
   ------------------------------------------------------------

--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "test_core/test_lib/test_format_traceback.py", line x, in exec_func
    func()
    ~~~~^^
  File "test_core/test_lib/test_format_traceback.py", line x, in multiline_obj_name
    raise ValueError()
ValueError'''


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
    assert not is_suppressed_habapp_file(
        '/opt/habapp/lib/python3.9/site-packages/HABApp/openhab/connection_logic/file.py')
