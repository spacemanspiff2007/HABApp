import time
from typing import List, Optional

import HABApp
from . import get_random_name, EventWaiter


class OpenhabTmpItem:
    def __init__(self, item_type: str, item_name: Optional[str] = None):
        self.type: str = item_type
        self.name = get_random_name(item_type) if item_name is None else item_name

    def __enter__(self) -> HABApp.openhab.items.OpenhabItem:
        return self.create()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()

    def remove(self):
        HABApp.openhab.interface.remove_item(self.name)

    def create(self, label="", category="", tags: List[str] = [], groups: List[str] = [],
               group_type: str = '', group_function: str = '',
               group_function_params: List[str] = []) -> HABApp.openhab.items.OpenhabItem:

        interface = HABApp.openhab.interface
        interface.create_item(self.type, self.name, label=label, category=category,
                              tags=tags, groups=groups, group_type=group_type,
                              group_function=group_function, group_function_params=group_function_params)

        # wait max 1 sec for the item to be created
        stop = time.time() + 1
        while not HABApp.core.Items.item_exists(self.name):
            time.sleep(0.01)
            if time.time() > stop:
                raise TimeoutError(f'Item {self.name} was not found!')

        return HABApp.openhab.items.OpenhabItem.get_item(self.name)

    def modify(self, label="", category="", tags: List[str] = [], groups: List[str] = [],
               group_type: str = '', group_function: str = '', group_function_params: List[str] = []):

        interface = HABApp.openhab.interface
        interface.create_item(self.type, self.name, label=label, category=category,
                              tags=tags, groups=groups, group_type=group_type,
                              group_function=group_function, group_function_params=group_function_params)

        with EventWaiter(self.name, HABApp.openhab.events.ItemUpdatedEvent) as w:
            w.wait_for_event()
