from typing import Annotated, Final

from pydantic import Discriminator, Tag
from pydantic import TypeAdapter as _TypeAdapter

from tests.helpers.code_gen.models.all_op import AllOperation
from tests.helpers.code_gen.models.literals import LiteralsOperation
from tests.helpers.code_gen.models.mixins import MixinsOperation
from tests.helpers.code_gen.models.select import SelectOperation
from tests.helpers.code_gen.models.separator import SeparatorOperation
from tests.helpers.code_gen.models.union import UnionOperation


def get_tag(x: dict | str) -> str:
    if x == 'all':
        return x
    if not len(x) == 1:
        raise ValueError()
    return next(iter(x))


InstructionType = Annotated[
    Annotated[SelectOperation, Tag('select')] |
    Annotated[MixinsOperation, Tag('mixins')] |
    Annotated[UnionOperation, Tag('union')] |
    Annotated[LiteralsOperation, Tag('literals')] |
    Annotated[SeparatorOperation, Tag('separator')] |
    Annotated[AllOperation, Tag('all')],
    Discriminator(get_tag)
]


InstructionTypeList = list[InstructionType]
InstructionTypeListAdapter: Final = _TypeAdapter(InstructionTypeList)
