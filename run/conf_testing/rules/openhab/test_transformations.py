from HABApp.openhab import transformations
from HABAppTests import TestBaseRule

obj = transformations.map['de.map']


class OpenhabTransformations(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('TestMap', self.test_map)

    def test_map(self):
        assert list(obj.keys())


OpenhabTransformations()
