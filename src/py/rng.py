import sys
INT_MAX = sys.maxsize

class RandomNumberGenerator:
    def __init__(self, seed):
        self.last = seed

    def LongInteger(self):
        k = self.last // 127773
        self.last = 16807 * (self.last - k   * 127773) - k * 2836
        if self.last < 0:
            self.last += INT_MAX

        return int(self.last)

    def IntegerInRange(self, min, max):
        return int(min + self.LongInteger() % (max - min + 1))

    def UnitReal(self):
        return self.LongInteger() * (1.0 / INT_MAX)

    def RealInRange(self, min, max):
        return min + (max - min) * self.UnitReal()
