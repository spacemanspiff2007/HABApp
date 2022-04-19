from HABApp.core.errors import HABAppException


class HABAppOpenhabError(HABAppException):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# Connection errors
# ----------------------------------------------------------------------------------------------------------------------
class OpenhabConnectionNotSetUpError(HABAppOpenhabError):
    pass


class OpenhabDisconnectedError(HABAppOpenhabError):
    pass


class ExpectedSuccessFromOpenhab(HABAppOpenhabError):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# OpenHAB errors
# ----------------------------------------------------------------------------------------------------------------------
class SendCommandNotSupported(HABAppOpenhabError):
    pass


class ItemNotFoundError(HABAppOpenhabError):

    @classmethod
    def from_name(cls, name: str):
        return cls(f'Item "{name}" not found!')


class ItemNotEditableError(HABAppOpenhabError):

    @classmethod
    def from_name(cls, name: str):
        return cls(f'Item "{name}" is not editable!')


class ThingNotFoundError(HABAppOpenhabError):

    @classmethod
    def from_uid(cls, uid: str):
        return cls(f'Thing "{uid}" not found!')


class ThingNotEditableError(HABAppOpenhabError):

    @classmethod
    def from_uid(cls, uid: str):
        return cls(f'Thing "{uid}" is not editable!')


# ----------------------------------------------------------------------------------------------------------------------
# RestAPI Errors
# ----------------------------------------------------------------------------------------------------------------------
class MetadataNotEditableError(HABAppOpenhabError):

    @classmethod
    def create_text(cls, item: str, namespace: str):
        return cls(f'Metadata {namespace} for {item} is not editable!')
