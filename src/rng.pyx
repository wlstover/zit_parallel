# rng.pyx
cdef long INT_MAX = 2147483647

cdef class RandomNumberGenerator:

    def __init__(self, long seed):
        self.last = seed
    
    cpdef long LongInteger(self):
        cdef long k
        k = self.last // 127773
        self.last = 16807 * (self.last - k   * 127773) - k * 2836
        if self.last < 0:
            self.last += INT_MAX

        return self.last
            
    cpdef long IntegerInRange(self, long min, long max):
        return int(min + self.LongInteger() % (max - min + 1))
 
    cpdef double UnitReal(self):
        return self.LongInteger() * (1.0 / INT_MAX)
    
    cpdef double RealInRange(self, double min, double max):
        return min + (max - min) * self.UnitReal()