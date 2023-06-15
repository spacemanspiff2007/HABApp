from HABAppTests import TestBaseRule
from HABAppTests.utils import find_astro_sun_thing

from HABApp.openhab.items import Thing
from time import sleep


class OpenhabThings(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('ApiDoc', self.test_api)
        self.add_test('Enable(API)', self.test_enabled_api)
        self.add_test('Enable(Obj)', self.test_enabled_obj)

    def test_api(self):
        self.openhab.get_thing(find_astro_sun_thing())

    def test_enabled_api(self):
        uid = find_astro_sun_thing()
        assert self.oh.set_thing_enabled(uid, False) == 200
        assert self.oh.set_thing_enabled(uid, True) == 200

    def test_enabled_obj(self):
        thing = Thing.get_item(find_astro_sun_thing())
        assert thing.is_enabled is True

        assert thing.set_enabled(False) == 200
        sleep(0.1)
        assert thing.is_enabled is False

        assert thing.set_enabled(True) == 200
        sleep(0.1)
        assert thing.is_enabled is True


OpenhabThings()
