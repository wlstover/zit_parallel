# rng.pyx
cdef public int INT_MAX = 2147483647

cdef class RandomNumberGenerator:
    cdef long last

    def __init__(self, long seed):
        self.last = seed

    cdef long LongInteger(self) nogil:
        cdef long k = self.last // 127773
        self.last = 16807 * (self.last - k * 127773) - k * 2836
        if self.last < 0:
            self.last += INT_MAX
        return self.last

    cdef int IntegerInRange(self, int min, int max) nogil:
        return min + self.LongInteger() % (max - min + 1)

    cdef double UnitReal(self) nogil:
        return self.LongInteger() * (1.0 / INT_MAX)

    cdef double RealInRange(self, double min, double max) nogil:
        return min + (max - min) * self.UnitReal()