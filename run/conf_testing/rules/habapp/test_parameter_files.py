from typing import Final

from HABAppTests import TestBaseRule

import HABApp
import HABApp.parameters


YAML_DATA: Final = {
    'int_key': 10,
    'str_key': 'test',
    'float_key': 1.2345,
}


# User uses Parameter files to create rules dynamically
assert HABApp.parameters.DictParameter('param_file') == YAML_DATA
assert HABApp.parameters.Parameter('param_file', 'int_key') == YAML_DATA['int_key']
assert HABApp.parameters.StrParameter('param_file', 'str_key') == YAML_DATA['str_key']

assert HABApp.parameters.IntParameter('param_file', 'int_key') == YAML_DATA['int_key']
assert HABApp.parameters.NumberParameter('param_file', 'int_key') == YAML_DATA['int_key']

assert HABApp.parameters.FloatParameter('param_file', 'float_key') == YAML_DATA['float_key']
assert HABApp.parameters.NumberParameter('param_file', 'float_key') == YAML_DATA['float_key']


class TestParamFile(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self) -> None:
        super().__init__()

        self.add_test('ParamFile', self.test_param_file)

    def test_param_file(self) -> None:
        p = HABApp.parameters.IntParameter('param_file', 'int_key')
        assert p.value == YAML_DATA['int_key']
        assert p < YAML_DATA['int_key'] + 1
        assert p > YAML_DATA['int_key'] - 1

        p = HABApp.parameters.DictParameter('param_file')
        assert p == YAML_DATA


TestParamFile()
