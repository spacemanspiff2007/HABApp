import gzip
import os
import shutil
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


class CompressedMidnightRotatingFileHandler(MidnightRotatingFileHandler):

    def __init__(self, *args, **kwargs):
        self.namer = self.compressedNamer
        self.rotator = self.compressedRotator
        super().__init__(*args, **kwargs)

    def compressedNamer(self, name):
        return name + ".gz"

    def compressedRotator(self, source, dest):
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(source)
