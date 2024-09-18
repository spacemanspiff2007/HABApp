
from msgspec import Struct


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest/src/main/java/org/openhab/core/io/rest/internal/resources/beans/SystemInfoBean.java


class SystemInfoResp(Struct, rename='camel', kw_only=True):
    config_folder: str
    userdata_folder: str
    log_folder: str | None = None
    java_version: str | None = None
    java_vendor: str | None = None
    java_vendor_version: str | None = None
    os_name: str | None = None
    os_version: str | None = None
    os_architecture: str | None = None
    available_processors: int
    free_memory: int
    total_memory: int
    start_level: int

    uptime: int = -1    # TODO: remove default if we go OH4.1 only


class SystemInfoRootResp(Struct, rename='camel'):
    system_info: SystemInfoResp
