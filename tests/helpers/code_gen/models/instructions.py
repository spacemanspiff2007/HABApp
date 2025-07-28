from typing import Annotated, Final

from pydantic import Discriminator, Tag
from pydantic import TypeAdapter as _TypeAdapter

from .mixins import MixinsOperation
from .select import SelectOperation
from .separator import SeparatorOperation
from .union import UnionOperation


def get_tag(x: dict) -> str:
    if not len(x) == 1:
        raise ValueError()
    return next(iter(x))


InstructionType = Annotated[
    Annotated[SelectOperation, Tag('select')] |
    Annotated[MixinsOperation, Tag('mixins')] |
    Annotated[UnionOperation, Tag('union')] |
    Annotated[SeparatorOperation, Tag('separator')],
    Discriminator(get_tag)
]


InstructionTypeList = list[InstructionType]
InstructionTypeListAdapter: Final = _TypeAdapter(InstructionTypeList)
