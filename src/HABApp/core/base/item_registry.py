from typing import Tuple, Union, TYPE_CHECKING, TypeVar

from HABApp.core.errors import ObjHasNotBeenReplacedError

if TYPE_CHECKING:
    import HABApp


def get_item(name: str) -> 'HABApp.core.base.TYPE_ITEM_OBJ':
    raise ObjHasNotBeenReplacedError(get_item)


class ItemRegistryBase:

    def item_exists(self, name: str) -> bool:
        raise NotImplementedError()

    def get_item(self, name: str) -> 'HABApp.core.base.TYPE_ITEM_OBJ':
        raise NotImplementedError()

    def get_items(self) -> Tuple['HABApp.core.base.TYPE_ITEM_OBJ', ...]:
        raise NotImplementedError()

    def get_item_names(self) -> Tuple[str, ...]:
        raise NotImplementedError()

    def add_item(self, item: 'HABApp.core.base.TYPE_ITEM_OBJ') -> 'HABApp.core.base.TYPE_ITEM_OBJ':
        raise NotImplementedError()

    def pop_item(self, name: Union[str, 'HABApp.core.base.TYPE_ITEM_OBJ']) -> 'HABApp.core.base.TYPE_ITEM_OBJ':
        raise NotImplementedError()

    # Todo: find a good way to implement and type hint this
    # def search_items(self, type: Union[Tuple[TYPE_ITEM_CLS, ...], TYPE_ITEM_CLS] = None,
    #                  name: Union[str, Pattern[str]] = None,
    #                  tags: Union[str, Iterable[str]] = None,
    #                  groups: Union[str, Iterable[str]] = None,
    #                  metadata: Union[str, Pattern[str]] = None,
    #                  metadata_value: Union[str, Pattern[str]] = None,
    #                  ) -> Union[List[TYPE_ITEM], List[BaseItem]]:
    #     raise NotImplementedError()


TYPE_ITEM_REGISTRY = TypeVar('TYPE_ITEM_REGISTRY', bound=ItemRegistryBase)
