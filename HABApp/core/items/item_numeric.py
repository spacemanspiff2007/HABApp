from . import Item


class NumericItem(Item):

    def __lt__(self, other):
        return self.state < other

    def __le__(self, other):
        return self.state <= other

    def __ge__(self, other):
        return self.state >= other

    def __gt__(self, other):
        return self.state > other
