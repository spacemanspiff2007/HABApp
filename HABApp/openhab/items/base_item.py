
class BaseItem:

    def __init__(self):
        self.name : str  = None
        self.state = None

    def __str__(self):
        return str(self.state)

    def update_state(self, _str):
        raise NotImplementedError()
