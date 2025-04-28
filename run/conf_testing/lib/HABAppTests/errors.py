class TestCaseFailed(Exception):  # noqa: N818
    def __init__(self, msg: str) -> None:
        self.msg = msg
