from pydantic import BaseModel, Field


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest/src/main/java/org/openhab/core/io/rest/internal/resources/beans/RootBean.java


class RuntimeResp(BaseModel):
    version: str
    build_string: str = Field(alias='buildString')


class LinkResp(BaseModel):
    type: str
    url: str


class RootResp(BaseModel):
    version: str
    locale: str
    measurement_system: str = Field(alias='measurementSystem')
    runtime_info: RuntimeResp = Field(alias='runtimeInfo')
    links: list[LinkResp]
