

# ----------------------------------------------------------------------------------------------------------------------
# Connection errors
# ----------------------------------------------------------------------------------------------------------------------
class OpenhabConnectionNotSetUpError(Exception):
    pass


class OpenhabDisconnectedError(Exception):
    pass


class OpenhabNotReadyYet(Exception):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# OpenHAB errors
# ----------------------------------------------------------------------------------------------------------------------
class ItemNotFoundError(Exception):

    @classmethod
    def from_name(cls, name: str):
        return cls(f'Item "{name}" not found!')


class ItemNotEditableError(Exception):

    @classmethod
    def from_name(cls, name: str):
        return cls(f'Item "{name}" is not editable!')


class ThingNotFoundError(Exception):

    @classmethod
    def from_uid(cls, uid: str):
        return cls(f'Thing "{uid}" not found!')


class ThingNotEditableError(Exception):

    @classmethod
    def from_uid(cls, uid: str):
        return cls(f'Thing "{uid}" is not editable!')


# ----------------------------------------------------------------------------------------------------------------------
# RestAPI Errors
# ----------------------------------------------------------------------------------------------------------------------
class MetadataNotEditableError(Exception):

    @classmethod
    def create_text(cls, item: str, namespace: str):
        return cls(f'Metadata {namespace} for {item} is not editable!')
