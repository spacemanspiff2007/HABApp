from typing import override

from tests.helpers.code_gen.models._base import BaseModel, BaseOperation
from tests.helpers.code_gen.models._select import SelectInputType, SelectInputTypeWithDefault
from tests.helpers.code_gen.models._text import TransformTextType
from tests.helpers.code_gen.module_context import ModuleContext


class MixinsModel(BaseModel):
    select: SelectInputType
    name: TransformTextType

    mixins: SelectInputTypeWithDefault


class MixinsOperation(BaseOperation):
    mixins: MixinsModel

    @override
    def execute(self, module: ModuleContext) -> str:
        mixins = self.mixins
        object_names = tuple(mixins.select.select_objects(module))
        mixin_names = tuple(mixins.mixins.select_objects(module))

        mixin_str = ', '.join(mixin_names)

        definitions = []
        for base_name in object_names:
            obj = f'class {mixins.name.transform(base_name):s}({base_name:s}, {mixin_str:s}):\n    pass'
            definitions.append(obj)

        return '\n\n\n'.join(definitions)
