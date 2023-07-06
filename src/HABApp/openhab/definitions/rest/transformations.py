from typing import Dict

from pydantic import BaseModel

# Documentation of TransformationDTO
# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.transform/src/main/java/org/openhab/core/io/rest/transform/TransformationDTO.java


class OpenhabTransformationDefinition(BaseModel):
    uid: str
    label: str
    type: str
    configuration: Dict[str, str]
    editable: bool
