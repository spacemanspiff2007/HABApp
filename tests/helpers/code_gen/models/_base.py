from typing import Annotated

from pydantic import BaseModel as _BaseModel
from pydantic import (
    ConfigDict,
    StringConstraints,
)

from tests.helpers.code_gen.module_context import ModuleContext


VarType = Annotated[str, StringConstraints(pattern=r'\w+')]


class BaseModel(_BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, validate_default=True, validate_assignment=True)


class BaseOperation(BaseModel):
    def execute(self, module: ModuleContext) -> str:
        raise NotImplementedError()
