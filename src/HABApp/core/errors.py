class HABAppException(Exception):
    pass


class ProxyObjHasNotBeenReplacedError(HABAppException):
    def __init__(self, obj) -> None:
        super().__init__(f'{obj} has not been replaced on startup!')


class ItemNotFoundException(HABAppException):
    def __init__(self, name: str):
        super().__init__(f'Item {name} does not exist!')
        self.name: str = name


class ItemAlreadyExistsError(HABAppException):
    def __init__(self, name: str):
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
