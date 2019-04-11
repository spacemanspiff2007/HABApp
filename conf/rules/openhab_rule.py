import HABApp
from HABApp.core.events import ValueUpdateEvent, ValueChangeEvent
from HABApp.openhab.events import ItemStateEvent, ItemCommandEvent, ItemStateChangedEvent

class MyOpenhabRule(HABApp.Rule):

    def __init__(self):
        super().__init__()

        # Trigger on item updates
        self.listen_event( 'TestContact', self.item_state_update, ItemStateEvent)
        self.listen_event( 'TestDateTime', self.item_state_update, ValueUpdateEvent)

        # Trigger on item changes
        self.listen_event( 'TestDateTime', self.item_state_change, ItemStateChangedEvent)
        self.listen_event( 'TestSwitch', self.item_state_change, ValueChangeEvent)

        # Trigger on item commands
        self.listen_event( 'TestSwitch', self.item_command, ItemCommandEvent)

    def item_state_update(self, event):
        assert isinstance(event, ValueUpdateEvent)
        print( f'{event}')

    def item_state_change(self, event):
        assert isinstance(event, ValueChangeEvent)
        print( f'{event}')

        # interaction is available through self.openhab or self.oh
        self.openhab.send_command('TestItemCommand', 'ON')

    def item_command(self, event):
        assert isinstance(event, ItemCommandEvent)
        print( f'{event}')

        # interaction is available through self.openhab or self.oh
        self.oh.post_update('TestItemUpdate', 123)


a = MyOpenhabRule()
