class HABAppException(Exception):
    pass


class ObjHasNotBeenReplacedError(HABAppException):
    def __init__(self, func: callable) -> None:
        super().__init__(f'Function {func.__name__} has not been replaced on startup!')


class ItemNotFoundException(HABAppException):
    def __init__(self, name: str):
        super().__init__(f'Item {name} does not exist!')
        self.name: str = name


class ItemAlreadyExistsError(HABAppException):
    def __init__(self, name: str):
        super().__init__(f'Item {name} does already exist and can not be added again!')
        self.name: str = name
