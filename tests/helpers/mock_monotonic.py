class MockedMonotonic:
    def __init__(self):
        self.time = 0

    def get_time(self):
        return self.time

    def __iadd__(self, other):
        self.time += other
        return self
