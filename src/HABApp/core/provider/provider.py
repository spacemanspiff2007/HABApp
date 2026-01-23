from __future__ import annotations

from asyncio import Lock
from typing import TYPE_CHECKING, Any, Final, Self, TypeVar

from HABApp.core.provider.type_helper import FactoryType, get_factory_type, get_obj_annotations, get_return_type


if TYPE_CHECKING:
    from types import TracebackType


T = TypeVar('T')


class ObjFactory:
    __slots__ = ('_close_obj', 'factory', 'provides', 'type')

    def __init__(self, factory: Any, provides: type, _type: FactoryType) -> None:
        self.factory: Final = factory
        self.provides: Final = provides
        self.type: Final = _type
        self._close_obj: Any = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} provides={self.provides} factory={self.factory} type={self.type}>'

    async def call(self, **kwargs: Any) -> object:
        args = []
        if isinstance(factory := self.factory, classmethod):
            args.append(factory.__class__)
            factory = factory.__func__

        if self.type == FactoryType.CALLABLE:
            return factory(*args, **kwargs)

        if self.type == FactoryType.COROUTINE:
            return await factory(*args, **kwargs)

        if self.type == FactoryType.SYNC_GENERATOR:
            self._close_obj = gen = factory(*args, **kwargs)
            return next(gen)

        if self.type == FactoryType.ASYNC_GENERATOR:
            self._close_obj = agen = factory(*args, **kwargs)
            return await agen.__anext__()

        if self.type == FactoryType.SYNC_CONTEXT_MANAGER:
            self._close_obj = obj = factory(*args, **kwargs)
            return obj.__enter__()

        if self.type == FactoryType.ASYNC_CONTEXT_MANAGER:
            self._close_obj = obj = factory(*args, **kwargs)
            return await obj.__aenter__()

        msg = f'Unsupported factory type: {self.type}'
        raise TypeError(msg)

    async def close(self, exception: BaseException | None = None) -> None:
        if self._close_obj is None:
            return None

        if self.type == FactoryType.SYNC_GENERATOR:
            try:  # noqa: SIM105
                self._close_obj.send(exception)
            except StopIteration:
                pass
        elif self.type == FactoryType.ASYNC_GENERATOR:
            try:  # noqa: SIM105
                await self._close_obj.asend(exception)
            except StopAsyncIteration:
                pass
        elif self.type == FactoryType.SYNC_CONTEXT_MANAGER:
            self._close_obj.__exit__(exception, None, None)
        elif self.type == FactoryType.ASYNC_CONTEXT_MANAGER:
            await self._close_obj.__aexit__(exception, None, None)
        else:
            msg = f'Unsupported close for factory type: {self.type}'
            raise TypeError(msg)

        return None


class HabAppObjProvider:
    __slots__ = ('_created', '_deferred', '_factories', '_lock', '_order')

    def __init__(self) -> None:
        self._factories: Final[dict[type, ObjFactory]] = {}
        self._created: Final[dict[type, object]] = {HabAppObjProvider: self}
        self._order: tuple[ObjFactory, ...] = ()

        self._lock: Final = Lock()
        self._deferred: tuple[type, ...] = ()

    def _add_factory(self, obj: type) -> None:

        _type = get_factory_type(obj)

        try:
            return_type = get_return_type(obj)
        except NameError:
            if obj not in self._factories:
                self._deferred += (obj, )
            return None

        if obj in self._deferred:
            self._deferred = tuple(x for x in self._deferred if x is not obj)

        if return_type in self._factories:
            existing = self._factories[return_type]
            msg = (f'Factory for type {return_type} is already registered:\n'
                   f'  {existing.factory} from {existing.factory.__module__}\n'
                   f'  {obj} from {obj.__module__}')
            raise ValueError(msg)

        if isinstance(return_type, str):
            msg = (f'Factory {obj} has a string return type "{return_type}" which is not supported.\n'
                   f'Did you forget "from __future__ import annotations"?')
            raise TypeError(msg)

        self._factories[return_type] = ObjFactory(factory=obj, provides=return_type, _type=_type)
        return None

    def register(self, obj: T) -> T:
        self._add_factory(obj)
        return obj

    async def _create(self, cls: type) -> object:

        if cls not in self._factories:
            msg = f'No factory registered for type {cls}'
            raise ValueError(msg)

        factory = self._factories[cls]
        dependencies = get_obj_annotations(factory.factory)

        kwargs = {}
        for name, dep_type in dependencies.items():
            kwargs[name] = await self._create(dep_type)

        self._created[cls] = obj = await factory.call(**kwargs)
        self._order += (factory, )
        return obj

    async def get(self, cls: type[T]) -> T:
        if cls in self._created:
            return self._created[cls]

        # try resolving deferred factories
        for obj in self._deferred:
            self._add_factory(obj)

        async with self._lock:
            return await self._create(cls)

    async def close(self, exception: BaseException | None = None) -> None:
        async with self._lock:
            order: Final = self._order
            self._order = ()
            self._created.clear()

            exceptions = []
            for factory in reversed(order):
                try:
                    await factory.close(exception)
                except Exception as e:
                    exceptions.append(e)

        if exceptions:
            msg = 'Errors during close()'
            raise ExceptionGroup(msg, exceptions)
        return None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None,
                        traceback: TracebackType | None) -> None:
        await self.close(exc_type)

    def has_factory(self, cls: type) -> bool:
        try:
            return cls in self._factories
        except TypeError:
            return False


HABAPP_PROVIDER: Final = HabAppObjProvider()
