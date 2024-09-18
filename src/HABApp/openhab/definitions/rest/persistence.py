from msgspec import Struct, field


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.persistence/src/main/java/org/openhab/core/persistence/dto/PersistenceServiceDTO.java
class PersistenceServiceResp(Struct):
    id: str
    label: str | None = None
    type: str | None = None


class DataPoint(Struct):
    time: int
    state: str


# ItemHistoryDTO
# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.persistence/src/main/java/org/openhab/core/persistence/dto/ItemHistoryDTO.java

class ItemHistoryResp(Struct):
    name: str
    total_records: str | None = field(default=None, name='totalrecords')
    data_points: str | None = field(default=None, name='datapoints')
    data: list[DataPoint] = []
