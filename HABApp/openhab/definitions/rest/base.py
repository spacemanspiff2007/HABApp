from typing import Any, Dict


class RestBase:
    def to_dict(self) -> Dict[str, Any]:
        return self.__pydantic_model__.dict(by_alias=True)

    @classmethod
    def from_dict(cls, _dict) -> 'RestBase':
        return cls.__pydantic_model__.parse_obj(_dict)
