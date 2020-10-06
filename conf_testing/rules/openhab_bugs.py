import time

from HABApp.openhab.connection_handler.func_async import async_create_item, async_get_item, ItemNotFoundError, \
    async_create_channel_link, async_remove_item
from HABAppTests import TestBaseRule, get_random_name, run_coro, find_astro_sun_thing


class BugLinks(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('delete item with link', self.create_meta)

    def create_meta(self):
        astro_thing = find_astro_sun_thing()
        astro_channel = f"{astro_thing}:rise#start"
        name = get_random_name()

        # create item and link
        run_coro(async_create_item('DateTime', name, 'MyCustomLabel', tags=['Tag1']))
        run_coro(async_create_channel_link(astro_channel, item_name=name))

        # get item
        run_coro(async_get_item(name))

        # delete it
        run_coro(async_remove_item(name))

        time.sleep(0.2)

        # it still exists but now with editable=False
        try:
            run_coro(async_get_item(name))
        except ItemNotFoundError:
            return True

        return False


# BugLinks()
