from typing import override

from tests.helpers.code_gen.module_context import ModuleContext

from . import SelectInputType, SelectInputTypeNoDefault
from ._base import BaseModel, BaseOperation
from .transform import TransformTextType


class MixinsModel(BaseModel):
    select: SelectInputType
    mixins: SelectInputTypeNoDefault

    name: TransformTextType


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
