import logging

import HABApp
from HABAppTests import TestBaseRule

log = logging.getLogger('HABApp.TestParameterFiles')

# User Parameter files to create rules dynamically
try:
    assert HABApp.parameters.get_parameter_value('param_file', 'key') != 10, \
        f'Loading of Parameters does not work properly'
except Exception as e:
    log.error(e)


class TestParamFile(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self):
        super().__init__()

        self.add_test('ParamFile', self.test_param_file)

    def test_param_file(self):
        p = HABApp.parameters.get_parameter('param_file', 'key')
        assert p < 11
        assert p.value == 10
    
        p = HABApp.parameters.RuleParameter('param_file', 'key')
        assert p < 11
        assert p.value == 10
        return True


TestParamFile()
