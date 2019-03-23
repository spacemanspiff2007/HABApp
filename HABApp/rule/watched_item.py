import datetime

from HABApp.core import Events, Items, ValueNoChangeEvent, ValueNoUpdateEvent


class WatchedItem:
    def __init__(self, name, constant_time, watch_only_changes = False):

        self.name = name
        self.const = datetime.timedelta(seconds=constant_time)
        self.executed = False

        self.__watch_only_changes = watch_only_changes

        self.is_canceled = False

    def check(self, now):
        if self.is_canceled:
            return None

        try:
            item = Items.get_item( self.name)
        except KeyError:
            return None

        timestamp = item.last_change if self.__watch_only_changes else item.last_update
        duration = now - timestamp
        if duration < self.const:
            self.executed = False
            return None

        if self.executed:
            return None

        Events.post_event(
            self.name,
            (ValueNoChangeEvent if self.__watch_only_changes else ValueNoUpdateEvent)
            (self.name, item.state, int(duration.total_seconds()))
        )
        self.executed = True

    def cancel(self):
        self.is_canceled = True
