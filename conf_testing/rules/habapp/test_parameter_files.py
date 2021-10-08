import logging

import HABApp
from HABAppTests import TestBaseRule

log = logging.getLogger('HABApp.TestParameterFiles')

# User Parameter files to create rules dynamically
try:
    assert HABApp.Parameter('param_file', 'key') == 10, \
        'Loading of Parameters does not work properly'
except Exception as e:
    log.error(e)
    log.error(HABApp.Parameter('param_file', 'key'))


class TestParamFile(TestBaseRule):
    """This rule is testing the Parameter implementation"""

    def __init__(self):
        super().__init__()

        self.add_test('ParamFile', self.test_param_file)

    def test_param_file(self):
        p = HABApp.Parameter('param_file', 'key')
        assert p < 11
        assert p.value == 10


TestParamFile()
