from pydantic import BaseModel, TypeAdapter


# Documentation of TransformationDTO
# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.transform/src/main/java/org/openhab/core/io/rest/transform/TransformationDTO.java

class TransformationResp(BaseModel):
    uid: str
    label: str
    type: str
    configuration: dict[str, str]
    editable: bool


TransformationRespList = TypeAdapter(tuple[TransformationResp, ...])
