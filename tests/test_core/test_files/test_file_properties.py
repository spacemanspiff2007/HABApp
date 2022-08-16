from HABApp.core.files.file.properties import get_properties as get_props
from HABApp.core.files.file.file import HABAppFile, CircularReferenceError, FileProperties, FILES, FileState
import pytest


def test_prop_case():
    _in = """# habapp:
    #   depends on:
    #    - my_Param.yml
    #   reloads on:
    #    - my_File.py
    #    - other_file.py
    """
    p = get_props(_in)
    assert p.depends_on == ['my_Param.yml']
    assert p.reloads_on == ['my_File.py', 'other_file.py']

    _in = """#
#     habapp:
#       depends on:
#        - my_Param.yml
#       reloads on:
#        - my_File.py
#        - other_file.py
"""
    p = get_props(_in)
    assert p.depends_on == ['my_Param.yml']
    assert p.reloads_on == ['my_File.py', 'other_file.py']


def test_prop_1():
    _in = """# HABApp:
#   depends on:
#    - my_Param.yml
#
#   reloads on:
#    - my_File.py
# This is my comment
#    - other_file.py
"""
    p = get_props(_in)
    assert p.depends_on == ['my_Param.yml']
    assert p.reloads_on == ['my_File.py']


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
    FILES.clear()
    FILES['name1'] = f1 = HABAppFile('name1', 'path1', FileProperties(depends_on=['name2']))
    FILES['name2'] = f2 = HABAppFile('name2', 'path2', FileProperties())

    f1.check_properties()
    f2.check_properties()

    assert f1.state is FileState.DEPENDENCIES_MISSING
    assert f2.state is FileState.DEPENDENCIES_OK

    f2.state = FileState.LOADED
    f1.check_dependencies()
    assert f1.state is FileState.DEPENDENCIES_OK


def test_reloads():
    FILES.clear()
    FILES['name1'] = f1 = HABAppFile('name1', 'path1', FileProperties(reloads_on=['name2', 'asdf']))
    FILES['name2'] = f2 = HABAppFile('name2', 'path2', FileProperties())

    f1.check_properties()
    assert f1.properties.reloads_on == ['name2', 'asdf']
    assert f2.properties.reloads_on == []


def test_circ():
    FILES.clear()
    FILES['name1'] = f1 = HABAppFile('name1', 'path1', FileProperties(depends_on=['name2']))
    FILES['name2'] = f2 = HABAppFile('name2', 'path2', FileProperties(depends_on=['name3']))
    FILES['name3'] = f3 = HABAppFile('name3', 'path3', FileProperties(depends_on=['name1']))

    with pytest.raises(CircularReferenceError) as e:
        f1._check_circ_refs((f1.name,), 'depends_on')
    assert e.value.stack == ('name1', 'name2', 'name3', 'name1')

    with pytest.raises(CircularReferenceError) as e:
        f2._check_circ_refs((f2.name,), 'depends_on')
    assert e.value.stack == ('name2', 'name3', 'name1', 'name2',)

    with pytest.raises(CircularReferenceError) as e:
        f3._check_circ_refs((f3.name,), 'depends_on')
    assert e.value.stack == ('name3', 'name1', 'name2', 'name3', )
