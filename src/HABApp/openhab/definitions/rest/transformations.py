from typing import Dict

from msgspec import Struct


# Documentation of TransformationDTO
# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.transform/src/main/java/org/openhab/core/io/rest/transform/TransformationDTO.java

class TransformationResp(Struct):
    uid: str
    label: str
    type: str
    configuration: Dict[str, str]
    editable: bool
