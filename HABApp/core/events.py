class AllEvents:
    pass


class ValueUpdateEvent:
    def __init__(self, name = None, value = None):
        self.name: str = name
        self.value = value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ValueChangeEvent:
    def __init__(self, name = None, value = None, old_value = None):
        self.name: str = name
        self.value = value
        self.old_value = old_value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ValueNoChangeEvent:
    def __init__(self, name = None, value = None, seconds = None):
        self.name: str = name
        self.value = value
        self.seconds: int = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, seconds: {self.seconds}>'


class ValueNoUpdateEvent:
    def __init__(self, name = None, value = None, seconds = None):
        self.name: str = name
        self.value = value
        self.seconds: int = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, seconds: {self.seconds}>'
