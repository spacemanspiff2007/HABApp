from typing import List

from msgspec import Struct

# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest/src/main/java/org/openhab/core/io/rest/internal/resources/beans/RootBean.java


class RuntimeResp(Struct, rename='camel'):
    version: str
    build_string: str


class LinkResp(Struct):
    type: str
    url: str


class RootResp(Struct, rename='camel'):
    version: str
    locale: str
    measurement_system: str
    runtime_info: RuntimeResp
    links: List[LinkResp]
