import HABApp
from HABApp.core.events import ValueUpdateEvent, ValueChangeEvent
from HABApp.openhab.events import ItemStateEvent, ItemCommandEvent, ItemStateChangedEvent
from HABApp.openhab.items import SwitchItem, ContactItem, DatetimeItem


class MyOpenhabRule(HABApp.Rule):

    def __init__(self):
        super().__init__()

        # get items
        test_contact = ContactItem.get_item('TestContact')
        test_date_time = DatetimeItem.get_item('TestDateTime')
        test_switch = SwitchItem.get_item('TestSwitch')

        # Trigger on item updates
        test_contact.listen_event(self.item_state_update, ItemStateEvent)
        test_date_time.listen_event(self.item_state_update, ValueUpdateEvent)

        # Trigger on item changes
        test_contact.listen_event(self.item_state_change, ItemStateChangedEvent)
        test_date_time.listen_event(self.item_state_change, ValueChangeEvent)

        # Trigger on item commands
        test_switch.listen_event(self.item_command, ItemCommandEvent)

    def item_state_update(self, event):
        assert isinstance(event, ValueUpdateEvent)
        print( f'{event}')

    def item_state_change(self, event):
        assert isinstance(event, ValueChangeEvent)
        print( f'{event}')

        # interaction is available through self.openhab or self.oh
        self.openhab.send_command('TestItemCommand', 'ON')

        # example for interaction with openhab item type
        switch_item = SwitchItem.get_item('TestSwitch')
        if switch_item.is_on():
            switch_item.off()

    def item_command(self, event):
        assert isinstance(event, ItemCommandEvent)
        print( f'{event}')

        # interaction is available through self.openhab or self.oh
        self.oh.post_update('ReceivedCommand', str(event))


MyOpenhabRule()
