from typing import Any as _Any
from typing_extensions import Self as _Self

from HABApp.core.const.hints import HasNameAttr as _HasNameAttr


class HABAppException(Exception):
    pass


class ProxyObjHasNotBeenReplacedError(HABAppException):
    def __init__(self, obj) -> None:
        super().__init__(f'{obj} has not been replaced on startup!')


class ItemNotFoundException(HABAppException):
    def __init__(self, name: str) -> None:
        super().__init__(f'Item {name} does not exist!')
        self.name: str = name


class ItemAlreadyExistsError(HABAppException):
    def __init__(self, name: str) -> None:
        super().__init__(f'Item {name} does already exist and can not be added again!')
        self.name: str = name


class ContextNotFoundError(HABAppException):
    pass


class ContextNotSetError(HABAppException):
    pass


class ContextBoundObjectIsAlreadyLinkedError(HABAppException):
    pass


class ContextBoundObjectIsAlreadyUnlinkedError(HABAppException):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# Value errors
# ----------------------------------------------------------------------------------------------------------------------
class HABAppValueError(ValueError, HABAppException):
    pass


class ItemValueIsNoneError(HABAppValueError):
    @classmethod
    def from_item(cls, item: _HasNameAttr) -> _Self:
        return cls(f'Item value is None (item "{item.name:s}")')


class InvalidItemValueError(HABAppValueError):
    @classmethod
    def from_item(cls, item: _HasNameAttr, value) -> _Self:
        return cls(f'Invalid value for {item.__class__.__name__} {item.name:s}: {value}')


# ----------------------------------------------------------------------------------------------------------------------
# Type errors
# ----------------------------------------------------------------------------------------------------------------------
class HABAppTypeError(TypeError, HABAppException):
    pass


class ItemNameNotOfTypeStrError(HABAppTypeError):
    @classmethod
    def from_value(cls, value: _Any) -> _Self:
        return cls(f'Item name must be of type str, not {type(value)}')


class WrongItemTypeError(HABAppTypeError):
    @classmethod
    def from_item(cls, item: _HasNameAttr, expected: type[object]) -> _Self:
        return cls(f'Item must be {expected.__name__}, not {item.__class__.__name__}')
