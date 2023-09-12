from HABApp.openhab.errors import LinkNotFoundError
from HABApp.openhab.items import Thing
from HABAppTests import TestBaseRule, find_astro_sun_thing


class TestOpenhabInterfaceLinks(TestBaseRule):
    def __init__(self):
        super().__init__()

        self.config.skip_on_failure = True

        self.item_name: str = ""
        self.astro_sun_thing: str = ""
        self.channel_uid: str = ""

        self.add_test("link creation", self.test_create_link)
        self.add_test("created link is gettable and equal", self.test_get_link)
        self.add_test("link existence", self.test_link_existence)
        self.add_test("link removal", self.test_remove_link)
        self.add_test("link update", self.test_update_link)

    def __create_test_item(self):
        self.openhab.create_item("Number", self.item_name)

    def set_up(self):
        self.item_name: str = "TestOpenhabInterfaceLinksItem"
        self.astro_sun_thing: str = find_astro_sun_thing()
        self.channel_uid: str = f"{self.astro_sun_thing}:rise#start"

        self.__create_test_item()
        if not self.openhab.item_exists(self.item_name):
            raise Exception("item could not be created")

    def tear_down(self):
        try:
            self.oh.get_link(self.item_name, self.channel_uid)
            self.oh.remove_link(self.item_name, self.channel_uid)
        except LinkNotFoundError:
            pass

        self.openhab.remove_item(self.item_name)

    def __find_astro_sun_thing(self) -> str:
        found_uid: str = ""
        for item in self.get_items(Thing, name='^astro:sun'):
            found_uid = item.name

        return found_uid

    def test_update_link(self):
        assert self.oh.create_link(self.item_name, self.channel_uid, {"profile": "system:default"})
        assert self.oh.get_link(self.item_name, self.channel_uid)

        new_cfg = {'profile': 'system:offset', 'offset': 7.0}
        assert self.oh.create_link(self.item_name, self.channel_uid, new_cfg)

        channel_link = self.oh.get_link(self.item_name, self.channel_uid)
        assert channel_link.configuration == new_cfg

    def test_get_link(self):
        target = {"profile": "system:default"}
        assert self.oh.create_link(self.item_name, self.channel_uid, target)
        link = self.oh.get_link(self.item_name, self.channel_uid)

        assert link.item == self.item_name
        assert link.channel == self.channel_uid
        assert link.configuration == target

    def test_remove_link(self):
        assert self.oh.create_link(self.item_name, self.channel_uid, {"profile": "system:default"})
        self.oh.remove_link(self.item_name, self.channel_uid)
        try:
            self.oh.get_link(self.item_name, self.channel_uid)
            assert False
        except LinkNotFoundError:
            pass

    def test_link_existence(self):
        assert self.oh.create_link(self.item_name, self.channel_uid, {"profile": "system:default"})
        assert self.oh.get_link(self.item_name, self.channel_uid)

        self.oh.remove_link(self.item_name, self.channel_uid)
        try:
            self.oh.get_link(self.item_name, self.channel_uid)
            assert False
        except LinkNotFoundError:
            pass

    def test_create_link(self):
        assert self.oh.create_link(self.item_name, self.channel_uid, {"profile": "system:default"})


TestOpenhabInterfaceLinks()
