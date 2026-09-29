from typing import override

from tests.helpers.code_gen.models._base import BaseOperation
from tests.helpers.code_gen.module_context import ModuleContext


class SeparatorOperation(BaseOperation):
    separator: bool | str

    @override
    def execute(self, module: ModuleContext) -> str:

        if isinstance(self.separator, bool) and self.separator:
            return '# ' + '-' * 118

        return (
            '# ' + '-' * 118 + '\n' +
            f'# {self.separator}' + '\n' +
            '# ' + '-' * 118
        )
