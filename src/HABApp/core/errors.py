class HABAppException(Exception):
    pass


class ItemNotFoundException(HABAppException):
    def __init__(self, name: str):
        super().__init__(f'Item {name} does not exist!')
        self.name: str = name


class ItemAlreadyExistsError(HABAppException):
    def __init__(self, name: str):
        super().__init__(f'Item {name} does already exist and can not be added again!')
        self.name: str = name
