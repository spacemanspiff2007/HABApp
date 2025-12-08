import re

from typing_extensions import override

from tests.helpers.code_gen.module_context import ModuleContext

from . import SelectInputType
from ._base import BaseModel, BaseOperation


ADAPTER_NAME_REGEX = re.compile('(?<=[a-z])([A-Z])')


class UnionModel(BaseModel):
    select: SelectInputType

    name: str
    discriminator: str | None = None
    adapter: bool = False


class UnionOperation(BaseOperation):
    union: UnionModel

    @override
    def execute(self, module: ModuleContext) -> str:
        union = self.union
        names = tuple(union.select.select_objects(module))

        discriminator = union.discriminator is not None

        seps = [' |' for _ in names]

        if discriminator:
            seps[-1] = ','
        else:
            seps[-1] = ''

        ret = [f'{union.name}: Final = {"Annotated[" if discriminator else "("}']

        for name, sep in zip(names, seps, strict=True):
            ret.append(f'    {name:s}{sep:s}')

        if discriminator:
            ret.append(f"    Field(discriminator='{union.discriminator}')")
            ret.append(']')
        else:
            ret.append(')')

        if union.adapter:
            adapter_name = ADAPTER_NAME_REGEX.sub(r'_\g<1>', union.name).upper().replace('OPEN_HAB', 'OPENHAB')
            adapter_line = f'{adapter_name}_ADAPTER: Final[TypeAdapter[{union.name}]] = TypeAdapter({union.name})'
            if len(adapter_line) > 120:
                adapter_line += '  # noqa: E501'
            ret.append(adapter_line)

        return '\n'.join(ret)
