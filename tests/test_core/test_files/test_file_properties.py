

from HABApp.core.files.file_properties import get_file_properties as get_props


def test_prop_case() -> None:
    _in = '''
    # habapp:
    #   depends on:
    #    - my_Param.yml
    #   reloads on:
    #    - my_File.py
    #    - other_file.py
    '''
    p = get_props(_in)
    assert p.depends_on == ['my_Param.yml']
    assert p.reloads_on == ['my_File.py', 'other_file.py']

    _in = '''#
#     habapp:
#       depends on:
#        - my_Param.yml
#       reloads on:
#        - my_File.py
#        - other_file.py
'''
    p = get_props(_in)
    assert p.depends_on == ['my_Param.yml']
    assert p.reloads_on == ['my_File.py', 'other_file.py']


def test_prop_1() -> None:
    _in = '''
# HABApp:
#   depends on:
#    - my_Param.yml
#
#   reloads on:
#    - my_File.py
# This is my comment
#    - other_file.py
'''
    p = get_props(_in)
    assert p.depends_on == ['my_Param.yml']
    assert p.reloads_on == ['my_File.py']


def test_prop_2() -> None:
    _in = '''

#
# HABApp:
#   depends on:
#    - my_param.yml
#
#

#   reloads on:
#    - my_file.py
# This is my comment
'''
    p = get_props(_in)
    assert p.depends_on == ['my_param.yml']
    assert p.reloads_on == []


def test_prop_3() -> None:
    _in = '''

#
# HABApp:
#   depends on:
#    - my_param1.yml
import asdf
#    - my_param2.yml
'''
    p = get_props(_in)
    assert p.depends_on == ['my_param1.yml']
    assert p.reloads_on == []


def test_prop_missing() -> None:
    _in = '''import bla bla bla
'''
    p = get_props(_in)
    assert p.depends_on == []
    assert p.reloads_on == []
