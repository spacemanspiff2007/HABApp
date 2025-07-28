from collections.abc import Sequence
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import Final, Generic, Self, TypeVar

import pytest

from HABApp.core.const import yml
from tests.helpers.code_gen.models import InstructionTypeList, InstructionTypeListAdapter
from tests.helpers.code_gen.module_context import ModuleContext


T = TypeVar('T')


class ListIterator(Generic[T]):
    def __init__(self, obj: Sequence[T]) -> None:
        self._obj: Final = obj
        self._pos: int = 0
        self._max_pos = len(self._obj)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(pos={self._pos:d})'

    def relative_seek(self, steps: int = 1) -> Self:
        self._pos = max(0, self._pos + steps)
        return self

    def peek(self, steps: int = 1) -> T:
        # peek(0) muss das aktuelle object zurück geben
        p = self._pos - 1 + steps
        if p >= self._max_pos:
            raise ValueError()
        if p < 0:
            raise ValueError()
        return self._obj[p]

    @property
    def pos(self) -> int:
        return self._pos

    def __next__(self) -> T:
        if (p := self._pos) >= self._max_pos:
            raise StopIteration

        obj = self._obj[p]
        self._pos = p + 1

        return obj

    def __iter__(self):
        return self


class CodeGenFile:
    COMMENT_SEPARATOR = '#' + '-' * 40

    def __init__(self, module: ModuleType, path: Path, text: str) -> None:
        self._module: Final = module
        self._path: Final = path
        self._text: Final = text
        self._new_text: str | None = None
        self.blocks: list[InstructionTypeList | str] = []

    def __repr__(self) -> str:
        return f'{self.__class__.__name__:s}(path={self._path})'

    def parse(self) -> Self:
        text_lines = self._text.splitlines()
        lines = ListIterator(
            tuple(zip((line.lower().replace(' ', '') for line in text_lines), text_lines, strict=True))
        )

        snip_start: int = 0
        for kw_line, line in lines:
            if not kw_line.startswith('#codegen'):
                continue

            if not lines.peek(-1)[0].startswith(self.COMMENT_SEPARATOR):
                continue

            if lines.peek()[0].startswith(self.COMMENT_SEPARATOR):
                lines.relative_seek()

            instructions = []
            for kw_line, line in lines:  # noqa: PLW2901
                if kw_line == '':
                    continue
                if kw_line.startswith('#'):
                    instructions.append(line)
                    continue

                lines.relative_seek(-1)
                break

            # reverse empty lines
            while lines.peek(0)[0] == '':
                lines.relative_seek(-1)

            # Save text and jump over generated code
            self.blocks.append('\n'.join(text_lines[snip_start: lines.pos]))

            for kw_line, _ in lines:  # noqa: PLW2901
                if kw_line.startswith(self.COMMENT_SEPARATOR):
                    lines.relative_seek(-1)
                    snip_start = lines.pos
                    break

            # remove separators in the beginning and at the end of the instructions
            while instructions[0].replace(' ', '').startswith(self.COMMENT_SEPARATOR):
                instructions.pop(0)
            while instructions[-1].replace(' ', '').startswith(self.COMMENT_SEPARATOR):
                instructions.pop()

            instruction = '\n'.join(line[line.index('#') + 1:] for line in instructions)
            instruction = dedent(instruction)
            instruction_yaml = yml.load(instruction)

            self.blocks.append(
                InstructionTypeListAdapter.validate_python(instruction_yaml)
            )

        return self

    def create(self) -> Self:

        context = ModuleContext(self._module)
        new_blocks: list[str] = []

        for obj in self.blocks:
            if isinstance(obj, str):
                new_blocks.append(obj)
                continue

            new_blocks.append(generate_code(context, obj))

        self._new_text = '\n'.join(new_blocks)
        return self

    def update(self) -> Self:
        if (new_text := self._new_text) is None:
            raise ValueError()

        if new_text == self._text:
            return None

        self._path.write_text(new_text)
        pytest.exit('New code generated')
        return self


def generate_code(module: ModuleContext, instructions: InstructionTypeList) -> str:
    lines: list[str] = []

    for instruction in instructions:
        if not (ret := instruction.execute(module)):
            continue

        lines.append('')
        lines.append('')
        lines.append(ret)

    lines.pop(0)
    lines.append('')
    return '\n'.join(lines)


def run_code_generator(module: ModuleType) -> None:
    path = Path(str(module.__file__))

    CodeGenFile(module, path, path.read_text()).parse().create().update()
    return None
