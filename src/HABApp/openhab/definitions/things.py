from HABApp.core.const.const import StrEnum
from typing import Final


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/ThingStatus.java
class ThingStatusEnum(StrEnum):
    UNINITIALIZED = 'UNINITIALIZED'
    INITIALIZING = 'INITIALIZING'
    UNKNOWN = 'UNKNOWN'
    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'
    REMOVING = 'REMOVING'
    REMOVED = 'REMOVED'


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/ThingStatusDetail.java
class ThingStatusDetailEnum(StrEnum):
    NONE = 'NONE'
    NOT_YET_READY = 'NOT_YET_READY'
    HANDLER_MISSING_ERROR = 'HANDLER_MISSING_ERROR'
    HANDLER_REGISTERING_ERROR = 'HANDLER_REGISTERING_ERROR'
    HANDLER_INITIALIZING_ERROR = 'HANDLER_INITIALIZING_ERROR'
    HANDLER_CONFIGURATION_PENDING = 'HANDLER_CONFIGURATION_PENDING'
    CONFIGURATION_PENDING = 'CONFIGURATION_PENDING'
    COMMUNICATION_ERROR = 'COMMUNICATION_ERROR'
    CONFIGURATION_ERROR = 'CONFIGURATION_ERROR'
    BRIDGE_OFFLINE = 'BRIDGE_OFFLINE'
    FIRMWARE_UPDATING = 'FIRMWARE_UPDATING'
    DUTY_CYCLE = 'DUTY_CYCLE'
    BRIDGE_UNINITIALIZED = 'BRIDGE_UNINITIALIZED'
    GONE = 'GONE'
    DISABLED = 'DISABLED'


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/internal/ThingImpl.java#L67
THING_STATUS_DEFAULT: Final = ThingStatusEnum.UNINITIALIZED
THING_STATUS_DETAIL_DEFAULT: Final = ThingStatusDetailEnum.NONE
