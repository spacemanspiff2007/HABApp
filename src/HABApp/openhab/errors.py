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


class OpenhabCredentialsInvalidError(HABAppOpenhabError):
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


# ----------------------------------------------------------------------------------------------------------------------
# Transformation errors
# ----------------------------------------------------------------------------------------------------------------------
class TransformationsRequestError(HABAppOpenhabError):
    pass


class MapTransformationError(HABAppOpenhabError):
    pass


class MapTransformationNotFound(HABAppOpenhabError):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# Persistence errors
# ----------------------------------------------------------------------------------------------------------------------
class PersistenceRequestError(HABAppOpenhabError):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# Link errors
# ----------------------------------------------------------------------------------------------------------------------
class LinkRequestError(HABAppOpenhabError):
    pass


class LinkNotFoundError(HABAppOpenhabError):
    @classmethod
    def from_names(cls, item: str, channel: str):
        return cls(f'Link {item:s} <-> {channel:s} not found!')


class LinkNotEditableError(HABAppOpenhabError):
    @classmethod
    def from_names(cls, item: str, channel: str):
        return cls(f'Link {item:s} <-> {channel:s} is not editable!')
