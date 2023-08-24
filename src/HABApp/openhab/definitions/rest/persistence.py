from typing import Optional, List

from msgspec import Struct, field


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.persistence/src/main/java/org/openhab/core/persistence/dto/PersistenceServiceDTO.java
class PersistenceServiceResp(Struct):
    id: str
    label: Optional[str] = None
    type: Optional[str] = None


class DataPoint(Struct):
    time: int
    state: str


# ItemHistoryDTO
# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.persistence/src/main/java/org/openhab/core/persistence/dto/ItemHistoryDTO.java

class ItemHistoryResp(Struct):
    name: str
    total_records: Optional[str] = field(default=None, name='totalrecords')
    data_points: Optional[str] = field(default=None, name='datapoints')
    data: List[DataPoint] = []
