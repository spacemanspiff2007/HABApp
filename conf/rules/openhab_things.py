import HABApp
from HABApp import Rule
from HABApp.openhab.events import ThingStatusInfoChangedEvent
from HABApp.openhab.items import Thing


class CheckAllThings(Rule):
    def __init__(self):
        super().__init__()
        
        for thing in HABApp.core.Items.get_all_items():
            if isinstance(thing, Thing):
                thing.listen_event(self.thing_status_changed, ThingStatusInfoChangedEvent)
                print(f'{thing.name}: {thing.status}')
    
    def thing_status_changed(self, event: ThingStatusInfoChangedEvent):
        print(f'{event.name} changed from {event.old_status} to {event.status}')


CheckAllThings()
