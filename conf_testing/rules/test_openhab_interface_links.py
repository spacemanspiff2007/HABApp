import HABApp
from HABApp.core.Items import get_all_items
from HABApp.openhab.definitions.rest import ItemChannelLinkDefinition, LinkNotFoundError
from HABApp.openhab.items import Thing
from conf_testing.lib.HABAppTests import ItemWaiter, OpenhabTmpItem, TestBaseRule, get_openhab_test_states, get_openhab_test_types

class TestOpenhabInterfaceLinks(TestBaseRule):
    def __init__(self):
        super().__init__()

        self.item_name: str = ""
        self.astro_sun_thing: str = ""
        self.channel_uid: str = ""

        self.add_test(f"link creation", self.test_create_link)
        self.add_test(f"created link is gettable and equal", self.test_get_link)
        self.add_test(f"link existence", self.test_link_existence)
        self.add_test(f"link removal", self.test_remove_link)
        self.add_test(f"link update", self.test_update_link)

    def __create_test_item(self):
        self.openhab.create_item("Number", self.item_name)

    def __get_link_def(self) -> ItemChannelLinkDefinition:
        return ItemChannelLinkDefinition(channelUID=self.channel_uid, itemName=self.item_name,
                                         configuration={"profile": "system:default"})

    def set_up(self):
        self.item_name: str = "TestOpenhabInterfaceLinksItem"
        self.astro_sun_thing: str = self.__find_astro_sun_thing()
        if self.astro_sun_thing == "":
            raise Exception("no astro:sun thing found")
        self.channel_uid: str = f"{self.astro_sun_thing}:rise:duration"

        self.__create_test_item()
        if not self.openhab.item_exists(self.item_name):
            raise Exception("item could not be created")

    def tear_down(self):
        if self.oh.link_exists(self.channel_uid, self.item_name):
            self.oh.remove_link(self.channel_uid, self.item_name)

        self.openhab.remove_item(self.item_name)

    def __find_astro_sun_thing(self) -> str:
        found_uid: str = ""
        for item in get_all_items():
            if isinstance(item, Thing) and item.name.startswith("astro:sun"):
                found_uid = item.name

        return found_uid

    def test_update_link(self):
        assert self.oh.create_link(self.__get_link_def())

        changed_def = self.__get_link_def()
        changed_def.configuration["profile"] = "system:offset"
        changed_def.configuration["offset"] = 7.0

        assert self.oh.create_link(changed_def)

        assert self.oh.get_link(self.channel_uid, self.item_name) == changed_def

    def test_get_link(self):
        assert self.oh.create_link(self.__get_link_def())
        link = self.oh.get_link(self.channel_uid, self.item_name)

        assert link == self.__get_link_def()

    def test_remove_link(self):
        assert self.oh.create_link(self.__get_link_def())
        
        assert self.oh.remove_link(self.channel_uid, self.item_name)

        assert not self.oh.link_exists(self.channel_uid, self.item_name)

    def test_link_existence(self):
        assert self.oh.create_link(self.__get_link_def())

        assert self.oh.link_exists(self.channel_uid, self.item_name)

        assert self.oh.remove_link(self.channel_uid, self.item_name)

        assert not self.oh.link_exists(self.channel_uid, self.item_name)

    def test_create_link(self):
        assert self.oh.create_link(self.__get_link_def())

TestOpenhabInterfaceLinks()
