import gzip
import shutil
from datetime import date, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class MidnightRotatingFileHandler(RotatingFileHandler):
    """A rotating file handler that checks once after midnight if the configured size has been exceeded and
    then rotates the file
    """

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
    """Same as ``MidnightRotatingFileHandler`` but rotates the file to a gzipped archive (``.gz``)

    """

    def __init__(self, *args, **kwargs):
        self.namer = self.compressed_namer
        self.rotator = self.compressed_rotator
        super().__init__(*args, **kwargs)

    def compressed_namer(self, default_name: str) -> str:
        return default_name + ".gz"

    def compressed_rotator(self, source: str, dest: str):
        src = Path(source)
        with src.open('rb') as f_in, gzip.open(dest, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        src.unlink()
