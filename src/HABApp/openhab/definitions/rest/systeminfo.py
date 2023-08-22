from typing import Optional

from msgspec import Struct


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest/src/main/java/org/openhab/core/io/rest/internal/resources/beans/SystemInfoBean.java


class SystemInfoResp(Struct, rename='camel', kw_only=True):
    config_folder: str
    userdata_folder: str
    log_folder: Optional[str] = None
    java_version: Optional[str] = None
    java_vendor: Optional[str] = None
    java_vendor_version: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    os_architecture: Optional[str] = None
    available_processors: int
    free_memory: int
    total_memory: int
    start_level: int


class SystemInfoRootResp(Struct, rename='camel'):
    system_info: SystemInfoResp
