from pydantic import BaseModel, Field, TypeAdapter


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.persistence/src/main/java/org/openhab/core/persistence/dto/PersistenceServiceDTO.java
class PersistenceServiceResp(BaseModel):
    id: str
    label: str | None = None
    type: str | None = None


PersistenceServiceRespList = TypeAdapter(tuple[PersistenceServiceResp, ...])


class DataPoint(BaseModel):
    time: int
    state: str


# ItemHistoryDTO
# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.persistence/src/main/java/org/openhab/core/persistence/dto/ItemHistoryDTO.java

class ItemHistoryResp(BaseModel):
    name: str
    total_records: str | None = Field(default=None, alias='totalrecords')
    data_points: str | None = Field(default=None, alias='datapoints')
    data: list[DataPoint] = []
