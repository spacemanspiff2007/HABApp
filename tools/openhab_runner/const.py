import logging
import sys


log = logging.getLogger('runner')
log_placeholder = logging.getLogger('placeholder')


def setup_logging() -> None:
    # Setup logging to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(0)
    handler.setFormatter(
        logging.Formatter('[{asctime:s}] [{name:11s}] {levelname:8s} | {message:s}', style='{')
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
