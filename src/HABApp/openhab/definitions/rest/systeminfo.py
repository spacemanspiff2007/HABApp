
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest/src/main/java/org/openhab/core/io/rest/internal/resources/beans/SystemInfoBean.java


class SystemInfoResp(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

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


class SystemInfoRootResp(BaseModel):
    system_info: SystemInfoResp = Field(alias='systemInfo')
