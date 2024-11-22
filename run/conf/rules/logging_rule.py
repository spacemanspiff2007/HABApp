import logging

import HABApp


log = logging.getLogger('MyRule')


class MyLoggingRule(HABApp.Rule):

    def __init__(self) -> None:
        super().__init__()

        # different levels are available
        log.debug('Debug Message')
        log.info('Info Message')
        log.warning('Warning Message')
        log.error('Error Message')


MyLoggingRule()
