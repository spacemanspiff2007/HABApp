import random
import string
import time

import HABApp


class OpenhabTmpItem:
    def __init__(self, item_name, item_type):
        self.item_name = item_name
        self.item_type = item_type

        if self.item_name is None:
            self.item_name = ''.join(random.choice(string.ascii_letters) for _ in range(20))

    def __enter__(self) -> HABApp.core.items.Item:
        interface = HABApp.openhab.oh_interface.get_openhab_interface()

        if not interface.item_exists(self.item_name):
            interface.create_item(self.item_type, self.item_name)

        # wait max 1 sec for the item to be created
        stop = time.time() + 1
        while not HABApp.core.Items.item_exists(self.item_name):
            time.sleep(0.01)
            if time.time() > stop:
                break

        return HABApp.core.Items.get_item(self.item_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        HABApp.openhab.oh_interface.get_openhab_interface().remove_item(self.item_name)
