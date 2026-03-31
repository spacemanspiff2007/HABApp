from enum import Enum
from typing import Final, override

from tests.helpers.code_gen.models._base import BaseModel, BaseOperation
from tests.helpers.code_gen.models._select import SelectInputType
from tests.helpers.code_gen.models._text import RegexSearchModel, TransformTextType
from tests.helpers.code_gen.module_context import ModuleContext


class LiteralModel(BaseModel):
    select: SelectInputType
    name: TransformTextType

    ignore_values: RegexSearchModel | None = None
    sort_values: bool = False


class EnumLiteralOperation(BaseOperation):
    literals: LiteralModel

    @override
    def execute(self, module: ModuleContext) -> str:

        enums: Final = self.literals.select.select_objects(module)
        definitions = []

        for enum_name, enum_type in enums.items():
            if not issubclass(enum_type, Enum):
                msg = f'Enum {enum_name} is not a subclass of Enum'
                raise TypeError(msg)

            name = f'{self.literals.name.transform(enum_name):s}'
            values = [f"'{v.value}'" for v in (enum_type if not self.literals.sort_values else sorted(enum_type))]

            # try single line
            line = f'{name:s} = Literal[{", ".join(values)}]\n'
            if len(line) <= 120:
                definitions.append(line)
                continue

            definition = [f'{name:s} = Literal[']
            for value in values:
                definition.append(f'    {value:s},')  # noqa: PERF401
            definition.append(']')
            definitions.append('\n'.join(definition))

        return '\n\n\n'.join(definitions)


LiteralsOperation = EnumLiteralOperation
