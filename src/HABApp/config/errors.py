class HABAppConfigError(Exception):
    pass


class AbsolutePathExpected(HABAppConfigError):
    pass


class InvalidConfigError(HABAppConfigError):
    pass
