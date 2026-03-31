from typing import override

from tests.helpers.code_gen.models._base import BaseOperation
from tests.helpers.code_gen.models._select import SelectModuleObjs
from tests.helpers.code_gen.module_context import ModuleContext


class SelectOperation(BaseOperation):
    select: SelectModuleObjs

    @override
    def execute(self, module: ModuleContext) -> str:
        self.select.select_objects(module)
        return ''
