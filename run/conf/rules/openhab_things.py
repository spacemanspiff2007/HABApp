from HABApp import Rule
from HABApp.core.events import EventFilter
from HABApp.openhab.events import ThingStatusInfoChangedEvent
from HABApp.openhab.items import Thing


class CheckAllThings(Rule):
    def __init__(self):
        super().__init__()

        for thing in self.get_items(Thing):
            thing.listen_event(self.thing_status_changed, EventFilter(ThingStatusInfoChangedEvent))
            print(f'{thing.name}: {thing.status}')

    def thing_status_changed(self, event: ThingStatusInfoChangedEvent):
        print(f'{event.name} changed from {event.old_status} to {event.status}')


CheckAllThings()
