import asyncio
import time
from collections.abc import Generator
from functools import wraps
from time import monotonic
from types import TracebackType
from typing import Any, NotRequired, TypedDict, Unpack

from typing_extensions import Self

import HABApp
from HABApp.core.asyncio import AsyncContextError, thread_context
from HABApp.openhab.definitions.topics import TOPIC_ITEMS
from HABApp.openhab.items import OpenhabItem

from . import EventWaiter, get_random_name


class ItemApiKwargs(TypedDict):
    label: NotRequired[str]
    category: NotRequired[str]
    tags: NotRequired[list[str]]
    groups: NotRequired[list[str]]
    group_type: NotRequired[str]
    group_function: NotRequired[str]
    group_function_params: NotRequired[list[str]]


class OpenhabTmpItemBase:
    @classmethod
    def _insert_kwargs(cls, item_type: str, name: str | None, kwargs: dict[str, Any], arg_name: str | None) -> Self:
        item = cls(item_type, name)
        if arg_name is not None:
            if arg_name in kwargs:
                msg = f'Arg {arg_name} already set!'
                raise ValueError(msg)
            kwargs[arg_name] = item
        return item

    def __init__(self, item_type: str, item_name: str | None = None) -> None:
        self._type: str = item_type
        self._name = get_random_name(item_type) if item_name is None else item_name

    @property
    def name(self) -> str:
        return self._name

    def _wait_until_item_exists(self) -> Generator[float, Any, Any]:
        # wait max 1 sec for the item to be created
        stop = monotonic() + 1.5
        while not HABApp.core.Items.item_exists(self.name):
            if monotonic() > stop:
                msg = f'Item {self.name} was not found!'
                raise TimeoutError(msg)

            yield 0.01


class OpenhabTmpItem(OpenhabTmpItemBase):
    @staticmethod
    def use(item_type: str, name: str | None = None, *, arg_name: str = 'item'):
        def decorator(func):
            @wraps(func)
            def new_func(*args, **kwargs):
                item = OpenhabTmpItem._insert_kwargs(item_type, name, kwargs, arg_name)
                try:
                    return func(*args, **kwargs)
                finally:
                    item.remove()

            return new_func

        return decorator

    @staticmethod
    def create(item_type: str, name: str | None = None, *, arg_name: str | None = None):
        def decorator(func):
            @wraps(func)
            def new_func(*args, **kwargs):

                with OpenhabTmpItem._insert_kwargs(item_type, name, kwargs, arg_name):
                    return func(*args, **kwargs)

            return new_func

        return decorator

    def __enter__(self) -> HABApp.openhab.items.OpenhabItem:
        return self.create_item()

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        self.remove()
        return False

    def remove(self) -> None:
        if thread_context.get(None) is None:
            raise AsyncContextError(self.remove)
        HABApp.openhab.interface_sync.remove_item(self.name)

    def _create(self, **kwargs: Unpack[ItemApiKwargs]) -> None:
        if thread_context.get(None) is None:
            raise AsyncContextError(self._create)

        interface = HABApp.openhab.interface_sync
        interface.create_item(self._type, self._name, **kwargs)

    def create_item(self, **kwargs: Unpack[ItemApiKwargs]) -> OpenhabItem:

        self._create(**kwargs)
        for delay in self._wait_until_item_exists():
            time.sleep(delay)
        return OpenhabItem.get_item(self.name)

    def modify(self, **kwargs: Unpack[ItemApiKwargs]) -> None:
        with EventWaiter(TOPIC_ITEMS, HABApp.core.events.EventFilter(HABApp.openhab.events.ItemUpdatedEvent)) as w:
            self._create(**kwargs)
            w.wait_for_event()


class AsyncOpenhabTmpItem(OpenhabTmpItemBase):
    @staticmethod
    def use(item_type: str, name: str | None = None, *, arg_name: str = 'item'):
        def decorator(func):
            @wraps(func)
            async def new_func(*args, **kwargs):
                item = AsyncOpenhabTmpItem._insert_kwargs(item_type, name, kwargs, arg_name)
                try:
                    return await func(*args, **kwargs)
                finally:
                    await item.remove()

            return new_func

        return decorator

    @staticmethod
    def create(item_type: str, name: str | None = None, *, arg_name: str | None = None):

        def decorator(func):
            @wraps(func)
            async def new_func(*args, **kwargs):

                async with AsyncOpenhabTmpItem._insert_kwargs(item_type, name, kwargs, arg_name):
                    return await func(*args, **kwargs)

            return new_func

        return decorator

    async def __aenter__(self) -> HABApp.openhab.items.OpenhabItem:
        return await self.create_item()

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        await self.remove()
        return False

    async def remove(self) -> None:
        await HABApp.openhab.interface_async.async_remove_item(self.name)

    async def _create(self, **kwargs: Unpack[ItemApiKwargs]) -> None:
        interface = HABApp.openhab.interface_async
        await interface.async_create_item(self._type, self._name, **kwargs)

    async def create_item(self, **kwargs: Unpack[ItemApiKwargs]) -> OpenhabItem:

        await self._create(**kwargs)
        for delay in self._wait_until_item_exists():
            await asyncio.sleep(delay)
        return OpenhabItem.get_item(self.name)

    async def modify(self, **kwargs: Unpack[ItemApiKwargs]) -> None:
        with EventWaiter(TOPIC_ITEMS, HABApp.core.events.EventFilter(HABApp.openhab.events.ItemUpdatedEvent)) as w:
            await self._create(**kwargs)
            await w.async_wait_for_event()
