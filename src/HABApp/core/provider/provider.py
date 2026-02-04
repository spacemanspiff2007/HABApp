from __future__ import annotations

from asyncio import Lock
from inspect import isclass
from typing import TYPE_CHECKING, Any, Final, Self, TypeVar

from HABApp.core.provider.type_helper import FactoryType, get_factory_type, get_obj_parameters, get_return_type


if TYPE_CHECKING:
    from types import TracebackType


class HABAppProviderError(Exception):
    pass


class FactoryAlreadyRegisteredError(HABAppProviderError):
    pass


class FactoryNotFoundError(HABAppProviderError):
    pass


class CyclicDependencyError(HABAppProviderError):
    @classmethod
    def from_stack(cls, stack: tuple[type, ...]) -> Self:
        msg = (f'Cyclic dependency: '
               f'{" -> ".join(s.__name__ if isclass(s) else str(s) for s in reversed(stack))}')
        return cls(msg)


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
            exc_type = type(exception) if exception else None
            self._close_obj.__exit__(exc_type, exception, None)
        elif self.type == FactoryType.ASYNC_CONTEXT_MANAGER:
            exc_type = type(exception) if exception else None
            await self._close_obj.__aexit__(exc_type, exception, None)
        else:
            msg = f'Unsupported close for factory type: {self.type}'
            raise TypeError(msg)

        return None


T = TypeVar('T')


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
            if obj not in self._deferred:
                self._deferred += (obj, )
            return None

        if obj in self._deferred:
            self._deferred = tuple(x for x in self._deferred if x is not obj)

        if return_type in self._factories:
            existing = self._factories[return_type]
            msg = (f'Factory for type {return_type} is already registered:\n'
                   f'  {existing.factory} from {existing.factory.__module__}\n'
                   f'  {obj} from {obj.__module__}')
            raise FactoryAlreadyRegisteredError(msg)

        if isinstance(return_type, str):
            msg = (f'Factory {obj} has a string return type "{return_type}" which is not supported.\n'
                   f'Did you forget "from __future__ import annotations"?')
            raise TypeError(msg)

        self._factories[return_type] = ObjFactory(factory=obj, provides=return_type, _type=_type)
        return None

    def register(self, obj: T) -> T:
        self._add_factory(obj)
        return obj

    def _resolve_deferred(self) -> None:
        for obj in self._deferred:
            self._add_factory(obj)

    async def _create(self, cls: type, stack: tuple[type, ...] = ()) -> object:
        # double check e.g. after acquiring the lock in case another coroutine created it in the meantime
        if cls in self._created:
            return self._created[cls]

        if cls not in self._factories:
            msg = f'No factory registered for type {cls}'
            raise FactoryNotFoundError(msg)

        if cls in stack:
            raise CyclicDependencyError.from_stack(stack + (cls, ))

        factory = self._factories[cls]
        dependencies = get_obj_parameters(factory.factory)

        kwargs = {}
        for name, dep_type in dependencies.items():
            if dep_type in self._created:
                kwargs[name] = self._created[dep_type]
            else:
                kwargs[name] = await self._create(dep_type, stack + (cls, ))

        self._created[cls] = obj = await factory.call(**kwargs)
        self._order += (factory, )
        return obj

    async def get(self, cls: type[T]) -> T:
        if cls in self._created:
            return self._created[cls]

        # try resolving deferred factories
        self._resolve_deferred()

        async with self._lock:
            return await self._create(cls)

    async def close(self, exception: BaseException | None = None) -> None:
        async with self._lock:
            order: Final = self._order
            self._order = ()
            self._created.clear()
            self._created[HabAppObjProvider] = self

            exceptions: Final[list[Exception]] = []
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
        # try resolving deferred factories
        self._resolve_deferred()

        try:
            return cls in self._factories
        except TypeError:
            return False

    def remove_factory(self, cls: type) -> None:
        # try resolving deferred factories
        self._resolve_deferred()

        if cls in self._created:
            msg = f'Object for {cls} is already created!'
            raise RuntimeError(msg)

        self._factories.pop(cls)
        return None

    def get_all_objects(self) -> tuple[object, ...]:
        return tuple(self._created.values())

    def add_object(self, obj: object, cls: type | None = None, *, override_factory: bool = False) -> None:
        """Temporarily add an object to the provider"""
        if cls is not None:
            cls = type(obj)

        if cls in self._created:
            msg = f'Object for {cls} is already created!'
            raise RuntimeError(msg)

        if self.has_factory(cls) and not override_factory:
            msg = f'Factory for {cls} is already registered!'
            raise RuntimeError(msg)

        self._created[cls] = obj
        return None

    async def create_all(self) -> None:
        """Create all registered objects"""

        # try resolving deferred factories
        self._resolve_deferred()

        dependencies: Final = {
            cls: frozenset(get_obj_parameters(f.factory).values())
            for cls, f in self._factories.items() if cls not in self._created
        }

        can_create = [[cls for cls, deps in dependencies.items() if not deps]]

        async with self._lock:
            # create in batches
            while can_create:
                # create batch
                for cls in can_create.pop():
                    await self._create(cls)

                # append next batch
                deps_available = frozenset(self._created)
                deps_ok = [
                    cls for cls, deps in dependencies.items()
                    if cls not in self._created and not (deps - deps_available)
                ]
                if deps_ok:
                    can_create.append(deps_ok)

            # If we hit something here we have a missing dependency
            # Requesting it will raise the appropriate exception
            for cls in self._factories:
                if cls in self._created:
                    continue
                await self._create(cls)

        return None


HABAPP_PROVIDER: Final = HabAppObjProvider()
