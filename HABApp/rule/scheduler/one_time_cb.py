from .base import ScheduledCallbackBase


class OneTimeCallback(ScheduledCallbackBase):

    def _calculate_next_call(self):
        if self.run_counter:
            self.is_finished = True
