class OpenhabEvent:

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        raise NotImplementedError()
