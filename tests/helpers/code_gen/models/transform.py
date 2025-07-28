from __future__ import annotations

import re
from re import Match, Pattern
from typing import Any, Self, override

from pydantic import PrivateAttr

from ._base import BaseModel


class TransformModel(BaseModel):
    search: str
    _pattern: Pattern  = PrivateAttr()

    def model_post_init(self, context: Any) -> Self:  # noqa: ARG002
        self._pattern = re.compile(self.search, re.IGNORECASE)
        return self

    def _get_match_text(self, m: Match, text: str) -> str:  # noqa: ARG002
        groups = m.groups()
        return ''.join(p for p in groups if p is not None)

    def transform(self, text: str) -> str:
        if (m := self._pattern.search(text)) is None:
            msg = f'Pattern {self._pattern.pattern} not found in "{text:s}"'
            raise ValueError(msg)

        if not (new_text := self._get_match_text(m, text)):
            raise ValueError()
        return new_text


class TransformReplaceModel(TransformModel):
    replace: str | None

    @override
    def _get_match_text(self, m: Match, text: str) -> str:
        if self.replace is not None:
            return self._pattern.sub(self.replace, text)
        return super()._get_match_text(m, text)


TransformTextType = TransformModel | TransformReplaceModel
