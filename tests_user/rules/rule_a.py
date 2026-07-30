from HABApp.core.events import ItemNoUpdateEvent
from HABApp.openhab.events import ItemCommandEvent, ItemCommandEventFilter
from HABApp.openhab.items import NumberItem, StringItem
from HABApp.rule import Rule, create_rule


class RuleA(Rule):
    def __init__(self, item_name: str) -> None:
        super().__init__()

        self.item_nr = NumberItem.get_item('nr_' + item_name)
        self.item_nr.watch_update(60).listen_event(self.item_const)
        self.item_nr.watch_update(120).listen_event(self.item_const)    # this never triggers because of the first watch

        self.item_str = StringItem.get_item('str_' + item_name)
        self.item_str.listen_event(self.item_command, ItemCommandEventFilter())

    def item_const(self, event: ItemNoUpdateEvent) -> None:
        if event.seconds == 60:
            self.item_nr.oh_post_update(self.item_nr + 1)

    async def item_command(self, event: ItemCommandEvent) -> None:
        self.item_str.oh_post_update('Updated ' + event.value)


create_rule(RuleA, 'ProductionItem')
