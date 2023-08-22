import time
from functools import wraps
from typing import List, Optional

import HABApp
from HABApp.openhab.definitions.topics import TOPIC_ITEMS
from . import get_random_name, EventWaiter


class OpenhabTmpItem:
    @staticmethod
    def use(type: str, name: Optional[str] = None, arg_name: str = 'item'):
        def decorator(func):
            @wraps(func)
            def new_func(*args, **kwargs):
                assert arg_name not in kwargs, f'arg {arg_name} already set'
                item = OpenhabTmpItem(type, name)
                try:
                    kwargs[arg_name] = item
                    return func(*args, **kwargs)
                finally:
                    item.remove()
            return new_func
        return decorator

    @staticmethod
    def create(type: str, name: Optional[str] = None, arg_name: Optional[str] = None):
        def decorator(func):
            @wraps(func)
            def new_func(*args, **kwargs):
                with OpenhabTmpItem(type, name) as f:
                    if arg_name is not None:
                        assert arg_name not in kwargs, f'arg {arg_name} already set'
                        kwargs[arg_name] = f
                    return func(*args, **kwargs)
            return new_func
        return decorator

    def __init__(self, item_type: str, item_name: Optional[str] = None):
        self.type: str = item_type
        self.name = get_random_name(item_type) if item_name is None else item_name

    def __enter__(self) -> HABApp.openhab.items.OpenhabItem:
        return self.create_item()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove()

    def remove(self):
        HABApp.openhab.interface_sync.remove_item(self.name)

    def _create(self, label="", category="", tags: List[str] = [], groups: List[str] = [],
                group_type: str = '', group_function: str = '',
                group_function_params: List[str] = []):
        interface = HABApp.openhab.interface_sync
        interface.create_item(self.type, self.name, label=label, category=category,
                              tags=tags, groups=groups, group_type=group_type,
                              group_function=group_function, group_function_params=group_function_params)

    def create_item(self, label="", category="", tags: List[str] = [], groups: List[str] = [],
                    group_type: str = '', group_function: str = '',
                    group_function_params: List[str] = []) -> HABApp.openhab.items.OpenhabItem:

        self._create(label=label, category=category, tags=tags, groups=groups, group_type=group_type,
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

        with EventWaiter(TOPIC_ITEMS, HABApp.core.events.EventFilter(HABApp.openhab.events.ItemUpdatedEvent)) as w:

            self._create(label=label, category=category, tags=tags, groups=groups, group_type=group_type,
                         group_function=group_function, group_function_params=group_function_params)

            w.wait_for_event()
