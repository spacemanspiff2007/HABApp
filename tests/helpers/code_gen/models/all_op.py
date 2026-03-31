
from types import ModuleType
from typing import Any, override

from pydantic import model_validator

from tests.helpers.code_gen.models._base import BaseOperation
from tests.helpers.code_gen.models._select import SelectInputType
from tests.helpers.code_gen.module_context import ModuleContext


class AllModel(BaseOperation):
    select: SelectInputType


class AllOperation(BaseOperation):
    all: AllModel | None = None

    @model_validator(mode='before')
    @classmethod
    def _allow_all(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data
        if isinstance(data, str) and data == 'all':
            return {}
        return data

    @override
    def execute(self, module: ModuleContext) -> str:
        if self.all is None:
            # default we exclude modules
            objs = {}
            for name, obj in module.get_objects().items():
                if isinstance(obj, ModuleType):
                    continue
                objs[name] = obj
        else:
            objs = self.all.select.select_objects(module)

        if not objs:
            msg = 'No objects found for __all__ operation'
            raise ValueError(msg)

        try:
            all_names = module.get_var('__all__')
        except KeyError:
            all_names = {}
            module.set_var('__all__', all_names)

        append = bool(all_names)

        used_objs = {name for name in objs if name not in all_names}
        all_names.update(dict.fromkeys(used_objs, bool))

        if not used_objs:
            msg = 'No objects left after removing existing'
            raise ValueError(msg)

        prefix = f'__all__ {"+" if append else "":s}= (\n    '
        return prefix + '\n    '.join(f"'{f:s}'," for f in sorted(used_objs)) + '\n)'
