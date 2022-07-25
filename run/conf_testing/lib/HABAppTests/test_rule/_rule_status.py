from enum import Enum, auto


class TestRuleStatus(Enum):
    CREATED = auto()
    PENDING = auto()
    RUNNING = auto()
    FINISHED = auto()
