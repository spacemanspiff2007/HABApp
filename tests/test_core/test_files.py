from HABApp.core.files.file_props import get_props


def test_prop_1():
    _in = """# HABApp:
#   depends on:
#    - my_param.yml
#
#   reload on:
#    - my_file.py
# This is my comment
#    - other_file.py
"""
    p = get_props(_in)
    assert p.depends_on == ['my_param.yml']
    assert p.reload_on == ['my_file.py']


def test_prop_2():
    _in = """

#
# HABApp:
#   depends on:
#    - my_param.yml
#
#

#   reload on:
#    - my_file.py
# This is my comment
"""
    p = get_props(_in)
    assert p.depends_on == ['my_param.yml']
    assert p.reload_on == []


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
    assert p.reload_on == []
