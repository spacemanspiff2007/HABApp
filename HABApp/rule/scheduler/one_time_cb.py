from .base import ScheduledCallbackBase, TYPING_DATE_TIME


class OneTimeCallback(ScheduledCallbackBase):

    def _calculate_next_call(self):
        if self.run_counter:
            self.is_finished = True

    def set_run_time(self, next_time: TYPING_DATE_TIME) -> 'OneTimeCallback':
        self._set_next_base(next_time)
        self._update_run_time()
        return self
