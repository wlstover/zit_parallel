cdef class Data:
    cdef public long N
    cdef public double min
    cdef public double max 
    cdef public double sum1
    cdef public sum2

    cpdef void AddDatum(self, double Datum)
    cpdef long GetN(self)

    cpdef double GetMin(self)
    cpdef double GetMax(self)
    cpdef double GetDelta(self)
    cpdef double GetAverage(self)
    cpdef double GetVariance(self)
    cpdef double GetStdDev(self)

cdef class DataVector:
    cdef list data

    cpdef void Clear(self)
    cpdef double L2StdDev(self)
    cpdef double LinfStdDev(self)