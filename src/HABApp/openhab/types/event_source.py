from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, NamedTuple, Self

from pydantic_core import core_schema

from HABApp.core.const import MISSING, MISSING_TYPE


if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import CoreSchema


class EventSourceComponent(NamedTuple):
    """A single (non-delegated) component of an :class:`EventSourceStr`.

    See `openHAB docs <https://www.openhab.org/docs/developer/utils/events.html#event-source>`_ for more information.

    :ivar bundle: Name of the bundle (in Java package name format) that sent resp. forwarded the event
    :ivar actor: Optional identifier (user, rule, device, ...) that caused the event
    """

    bundle: str
    actor: str | None

    def __str__(self) -> str:
        if self.actor is None:
            return self.bundle
        return f'{self.bundle}${self.actor}'


def _parse_component(value: str) -> tuple[str, str | None]:
    # HABApp uses a fixed convention for its own sources: "HABApp.<actor>" (bundle "HABApp" separated by "."
    # instead of the regular "$"). We parse it like any other source, so there is no need to treat it differently.
    if value.startswith('HABApp.'):
        return 'HABApp', value.removeprefix('HABApp.') or None

    # Bundle names can't contain the "$" (actor) separator -> partition on the first occurrence is unambiguous
    bundle, sep, actor = value.partition('$')
    return bundle, actor if sep else None


def _parse_components(value: str) -> tuple[EventSourceComponent, ...]:
    if not value:
        return ()

    # Fast path: the overwhelming majority of sources are not delegated
    if '=>' not in value:
        return (EventSourceComponent(*_parse_component(value)),)

    return tuple(EventSourceComponent(*_parse_component(part)) for part in value.split('=>'))


class EventSourceStr(str):
    """A string type specifically for event sources.

    The source identifies the sender of an openHAB event. It's structured as a (possibly empty) chain of
    delegated components, separated by ``=>``. Each component consists of a bundle name and an optional actor,
    separated by ``$`` (e.g. ``bundle_name$actor_name``).

    See `openHAB docs <https://www.openhab.org/docs/developer/utils/events.html#event-source>`_ for more information.
    """

    __slots__ = ('_actor', '_bundle', '_components')

    _bundle: str | MISSING_TYPE | None
    _actor: str | MISSING_TYPE | None
    _components: tuple[EventSourceComponent, ...] | MISSING_TYPE

    def __new__(cls, value: str) -> Self:
        if not isinstance(value, str):
            msg = f'Expected str, got {type(value)} for {cls.__name__}'
            raise TypeError(msg)

        obj: Final[Self] = super().__new__(cls, value)

        # bundle/actor/components are cached
        obj._bundle = MISSING
        obj._actor = MISSING
        obj._components = MISSING
        return obj

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        # Parse like a normal str and then cast the result to this class
        return core_schema.no_info_after_validator_function(cls, handler(str))

    def _parse_origin(self) -> tuple[str | None, str | None]:
        # Only the part up to the first delegation (if any) is relevant for bundle/actor
        first, _sep, _rest = self.partition('=>')
        bundle, actor = _parse_component(first) if first else (None, None)
        self._bundle = bundle
        self._actor = actor
        return bundle, actor

    @property
    def bundle(self) -> str | None:
        """Name of the bundle that (originally) caused the event, or ``None`` if the source is empty"""
        bundle = self._bundle
        if bundle is MISSING:
            bundle, _actor = self._parse_origin()
        return bundle

    @property
    def actor(self) -> str | None:
        """Optional actor of the bundle that (originally) caused the event (or ``None``)"""
        actor = self._actor
        if actor is MISSING:
            _bundle, actor = self._parse_origin()
        return actor

    @property
    def origin(self) -> EventSourceComponent | None:
        """The first (i.e. originating) component of the source or ``None`` if the source is empty"""
        bundle = self.bundle
        return EventSourceComponent(bundle, self.actor) if bundle is not None else None

    @property
    def components(self) -> tuple[EventSourceComponent, ...]:
        """The individual, ordered components of the (possibly delegated) source.

        The first component is the component that originally created the event, the last component is the
        component that (finally) sent/forwarded it. If the source is not delegated there is only one component.
        """
        components = self._components
        if components is MISSING:
            components = self._components = _parse_components(self)
        return components

    @property
    def is_delegated(self) -> bool:
        """``True`` if the source consists of more than one (delegated) component"""
        return len(self.components) > 1
