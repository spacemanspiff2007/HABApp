from HABApp.core.files.file_props import get_props
from HABApp.core.files.file import HABAppFile, CircularReferenceError, FileProperties, ALL
import pytest


def test_prop_1():
    _in = """# HABApp:
#   depends on:
#    - my_param.yml
#
#   reloads on:
#    - my_file.py
# This is my comment
#    - other_file.py
"""
    p = get_props(_in)
    assert p.depends_on == ['my_param.yml']
    assert p.reloads_on == ['my_file.py']


def test_prop_2():
    _in = """

#
# HABApp:
#   depends on:
#    - my_param.yml
#
#

#   reloads on:
#    - my_file.py
# This is my comment
"""
    p = get_props(_in)
    assert p.depends_on == ['my_param.yml']
    assert p.reloads_on == []


def test_prop_3():
    _in = """

#
# HABApp:
#   depends on:
#    - my_param1.yml
import asdf
#    - my_param2.yml
"""
    p = get_props(_in)
    assert p.depends_on == ['my_param1.yml']
    assert p.reloads_on == []


def test_prop_missing():
    _in = """import bla bla bla
"""
    p = get_props(_in)
    assert p.depends_on == []
    assert p.reloads_on == []


def test_deps():
    ALL.clear()
    ALL['name1'] = f1 = HABAppFile('name1', 'path1', FileProperties(depends_on=['name2']))
    ALL['name2'] = f2 = HABAppFile('name2', 'path2', FileProperties())

    f1.check_properties()
    f2.check_properties()

    assert f2.can_be_loaded()
    assert not f1.can_be_loaded()

    f2.is_loaded = True
    assert f1.can_be_loaded()


def test_reloads():
    ALL.clear()
    ALL['name1'] = f1 = HABAppFile('name1', 'path1', FileProperties(reloads_on=['name2', 'asdf']))
    ALL['name2'] = f2 = HABAppFile('name2', 'path2', FileProperties())

    f1.check_properties()
    assert f1.properties.reloads_on == ['name2']


def test_circ():
    ALL.clear()
    ALL['name1'] = f1 = HABAppFile('name1', 'path1', FileProperties(depends_on=['name2']))
    ALL['name2'] = f2 = HABAppFile('name2', 'path2', FileProperties(depends_on=['name3']))
    ALL['name3'] = f2 = HABAppFile('name3', 'path3', FileProperties(depends_on=['name1']))

    with pytest.raises(CircularReferenceError) as e:
        f1.check_properties()
    assert str(e.value) == "name1 -> name2 -> name3 -> name1"
