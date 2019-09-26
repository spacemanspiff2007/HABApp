import pytest

from HABApp.parameters.rule_parameter import RuleParameter
import HABApp.parameters.parameters as Parameters


@pytest.fixture(scope="function")
def params():
    Parameters.ParameterFileWatcher.UNITTEST = True
    Parameters.setup(None, None)
    yield None
    Parameters._PARAMETERS.clear()


def test_lookup(params):

    data = {'key1': {'key2': 'value2'}}
    Parameters.set_parameter_file('file1', data)
    p = RuleParameter('file1', 'key1', 'key2')
    assert p == 'value2'

    data['key1']['key2'] = 3
    assert p == 3


def test_int_operators(params):
    Parameters.set_parameter_file('file', {'key': 5})
    p = RuleParameter('file', 'key')
    assert p == 5
    assert p != 6

    assert p < 6
    assert p <= 5
    assert p >= 5
    assert p > 4

    Parameters.set_parameter_file('file', {'key': 15})
    assert not p < 6
    assert not p <= 5
    assert p >= 5
    assert p > 4


def test_float_operators(params):
    Parameters.set_parameter_file('file', {'key': 5.5})
    p = RuleParameter('file', 'key')

    assert p < 6
    assert not p <= 5
    assert p >= 5
    assert p > 4


def test_simple_key_creation(params):

    RuleParameter('file', 'key')
    assert Parameters.get_parameter_file('file') == {'key': 'ToDo'}

    RuleParameter('file', 'key2')
    assert Parameters.get_parameter_file('file') == {'key': 'ToDo', 'key2': 'ToDo'}


def test_structured_key_creation(params):
    RuleParameter('file', 'key1', 'key1')
    RuleParameter('file', 'key1', 'key2')
    assert Parameters.get_parameter_file('file') == {'key1': {'key1': 'ToDo', 'key2': 'ToDo'}}


def test_structured_default_value(params):
    RuleParameter('file', 'key1', 'key1', default_value=123)
    RuleParameter('file', 'key1', 'key2', default_value=[1, 2, 3])
    assert Parameters.get_parameter_file('file') == {'key1': {'key1': 123, 'key2': [1, 2, 3]}}
