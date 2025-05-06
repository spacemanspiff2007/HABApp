from collections.abc import Generator
from typing import Final, Generic, Literal, TypeVar, overload

from typing_extensions import Self
from whenever import Instant, TimeDelta

from HABApp.core.const import MISSING, MISSING_TYPE


K = TypeVar('K')
V = TypeVar('V')


class ExpiringCache(Generic[K, V]):
    def __init__(self, expiry_time: float) -> None:
        self._cache: Final[dict[K, tuple[V, Instant]]] = {}
        self._expiry_time: TimeDelta = TimeDelta.ZERO

        self.set_expiry_time(expiry_time)

    def set_expiry_time(self, expiry_time: float | TimeDelta) -> None:
        """Set the expiry time for cache entries.

        :param expiry_time: expire duration
        """

        if isinstance(expiry_time, (int, float)):
            expiry_time = TimeDelta(seconds=expiry_time)

        if not isinstance(expiry_time, TimeDelta):
            raise TypeError()

        if expiry_time <= TimeDelta.ZERO:
            msg = 'Expiry time must be greater than 0'
            raise ValueError(msg)

        self._expiry_time = expiry_time

    def flush(self) -> Self:
        """Flush all expired entries out of the cache"""

        rem = []
        min_age = Instant.now() - self._expiry_time
        for key, (_, instant) in self._cache.items():
            if instant < min_age:
                rem.append(key)

        for key in rem:
            del self._cache[key]

        return self

    def reset(self, key: K) -> Self:
        """Reset the expiry time of a cache entry (if available)

        :param key: key of entry
        """
        if (obj := self._cache.get(key)) is None:
            return self

        self._cache[key] = obj[0], Instant.now()
        return self

    def set_expired(self, key: K) -> Self:
        """Set a cache entry expired (if available)

        :param key: key of entry
        """
        if (obj := self._cache.get(key)) is None:
            return self

        self._cache[key] = obj[0], Instant.now().subtract(nanoseconds=1) - self._expiry_time
        return self

    def is_expired(self, key: K) -> bool:
        """Check if a cache entry is expired

        :param key: key of entry
        """
        value, instant = self._cache[key]
        return Instant.now() > instant + self._expiry_time

    def in_cache(self, key: K) -> bool:
        """Check if a cache entry is in the cache

        :param key: key of entry
        """
        return key in self._cache

    def __iter(self, mode: Literal['all', 'expired', 'not_expired']) -> Generator[tuple[K, V], None, None]:
        if mode == 'all':
            for key, (value, _) in self._cache.items():
                yield key, value
            return None

        ret_expired = mode == 'expired'

        for key, (value, instant) in self._cache.items():
            is_expired = instant < Instant.now() - self._expiry_time

            if ret_expired:
                is_expired = not is_expired

            if not is_expired:
                yield key, value

    def set(self, key: K, value: V) -> Self:
        """Set a value in the cache

        :param key: key
        :param value: value
        """
        self._cache[key] = (value, Instant.now())
        return self

    def __setitem__(self, key: K, value: V) -> None:
        self._cache[key] = (value, Instant.now())

    @overload
    def get(self, key: K, default: V) -> V:
        ...

    @overload
    def get(self, key: K, default: None = None) -> V | None:
        ...

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get a value from the cache, or return the default value if not found or expired

        :param key: key
        :param default: default
        """
        if (obj := self._cache.get(key)) is None:
            return default

        value, instant = obj
        if Instant.now() <= instant + self._expiry_time:
            return value

        return default

    @overload
    def pop(self, key: K) -> V:
        ...

    @overload
    def pop(self, key: K, default: V) -> V:
        ...

    @overload
    def pop(self, key: K, default: None) -> V | None:
        ...

    def pop(self, key: K, default: V | None | MISSING_TYPE = MISSING) -> V | None:
        """Get a value from the cache, or return the default value if not found or expired

        :param key: key
        :param default: optional default
        :return:
        """
        if (obj := self._cache.pop(key, MISSING)) is not MISSING:
            value, instant = obj
            if Instant.now() <= instant + self._expiry_time:
                return value

        if default is MISSING:
            raise KeyError(key)
        return default

    # ------------------------------------------------------------------------------------------------------------------
    # Dict interface only for values that are not expired
    # ------------------------------------------------------------------------------------------------------------------
    def __getitem__(self, key: K) -> V:
        """Get the value from the cache."""
        value, instant = self._cache[key]
        if Instant.now() <= instant + self._expiry_time:
            return value

        raise KeyError(key)

    def __contains__(self, key: K) -> bool:
        if (obj := self._cache.get(key)) is None:
            return False
        return Instant.now() <= obj[1] + self._expiry_time

    # ------------------------------------------------------------------------------------------------------------------
    # Dict interface
    # ------------------------------------------------------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._cache)

    def __delitem__(self, key: K) -> None:
        del self._cache[key]

    def __iter__(self) -> Generator[K, None, None]:
        for k, _ in self.__iter('not_expired'):
            yield k

    def keys(self, mode: Literal['all', 'expired', 'not_expired'] = 'not_expired') -> Generator[K, None, None]:
        """Get all keys in the cache that are not expired

        :param mode: ``not_expired`` - only keys of items which are not expired,
                     ``expired`` - only expired items,
                     ``all`` - all items
        """
        for k, _ in self.__iter(mode):
            yield k

    def values(self, mode: Literal['all', 'expired', 'not_expired'] = 'not_expired') -> Generator[V, None, None]:
        """Get all values in the cache that are not expired

        :param mode: ``not_expired`` - only values of items which are not expired,
                     ``expired`` - only expired items,
                     ``all`` - all items
        """
        for _, v in self.__iter(mode):
            yield v

    def items(self,
              mode: Literal['all', 'expired', 'not_expired'] = 'not_expired') -> Generator[tuple[K, V], None, None]:
        """Get all items in the cache that are not expired

        :param mode: ``not_expired`` - only items which are not expired,
                     ``expired`` - only expired items,
                     ``all`` - all items
        """
        yield from self.__iter(mode)
