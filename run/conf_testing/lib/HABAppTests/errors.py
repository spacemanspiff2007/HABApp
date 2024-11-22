class TestCaseFailed(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg


class TestCaseWarning(Exception):
    def __init__(self, msg: str) -> None:
        self.msg = msg
