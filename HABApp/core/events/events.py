from typing import Any, Union


class AllEvents:
    pass


class ComplexEventValue:
    def __init__(self, value):
        self.value: Any = value


class ValueUpdateEvent:
    name: str
    value: Any

    def __init__(self, name=None, value=None):
        self.name: str = name
        self.value = value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ValueChangeEvent:
    name: str
    value: Any
    old_value: Any

    def __init__(self, name=None, value=None, old_value=None):
        self.name: str = name
        self.value = value
        self.old_value = old_value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ItemNoChangeEvent:
    name: str
    seconds: Union[int, float]

    def __init__(self, name=None, seconds=None):
        self.name: str = name
        self.seconds: int = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, seconds: {self.seconds}>'


class ItemNoUpdateEvent:
    name: str
    seconds: Union[int, float]

    def __init__(self, name=None, seconds=None):
        self.name: str = name
        self.seconds: int = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, seconds: {self.seconds}>'
