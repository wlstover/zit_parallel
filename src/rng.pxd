# rng.pxd
cdef class RandomNumberGenerator:
    cdef public long last

    cpdef long LongInteger(self)
    cpdef long IntegerInRange(self, long min, long max)
    cpdef double UnitReal(self)
    cpdef double RealInRange(self, double min, double max)