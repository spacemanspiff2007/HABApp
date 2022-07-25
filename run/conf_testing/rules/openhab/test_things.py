from HABAppTests import TestBaseRule
from HABAppTests.utils import find_astro_sun_thing


class OpenhabThings(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('ApiDoc', self.test_api)

    def test_api(self):
        self.openhab.get_thing(find_astro_sun_thing())


OpenhabThings()
