from typing import Any, Union, Final


class ComplexEventValue:
    def __init__(self, value):
        self.value: Any = value


class ValueUpdateEvent:
    """
    :ivar str name:
    :ivar Any value:
    """

    name: str
    value: Any

    def __init__(self, name: str, value: Any):
        self.name: Final = name
        self.value: Final = value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ValueChangeEvent:
    """
    :ivar str name:
    :ivar Any value:
    :ivar Any old_value:
    """

    name: str
    value: Any
    old_value: Any

    def __init__(self, name: str, value: Any, old_value: Any):
        self.name: Final = name
        self.value: Final = value
        self.old_value: Final = old_value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ItemNoChangeEvent:
    """
    :ivar str               name:
    :ivar Union[int, float] seconds:
    """

    name: str
    seconds: Union[int, float]

    def __init__(self, name: str, seconds: Union[int, float]):
        self.name: Final = name
        self.seconds: Final = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, seconds: {self.seconds}>'


class ItemNoUpdateEvent:
    """
    :ivar str               name:
    :ivar Union[int, float] seconds:
    """
    name: str
    seconds: Union[int, float]

    def __init__(self, name: str, seconds: Union[int, float]):
        self.name: Final = name
        self.seconds: Final = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, seconds: {self.seconds}>'
