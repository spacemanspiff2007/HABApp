from datetime import date, datetime
from logging.handlers import RotatingFileHandler


class MidnightRotatingFileHandler(RotatingFileHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_check: date = datetime.now().date()

    def shouldRollover(self, record):
        date = datetime.now().date()
        if date == self.last_check:
            return 0
        self.last_check = date
        return super().shouldRollover(record)
