from libc.math cimport sqrt

cdef DataVectorSize = 100

cdef class Data:

    def __init__(self):
        self.N = 0
        self.min = 1000000.0
        self.max = 0.0
        self.sum1 = 0.0
        self.sum2 = 0.0
        
    cpdef void AddDatum(self, double Datuum):
        self.N += 1
        if Datuum < self.min:
            self.min = Datuum
        elif Datuum > self.max:
            self.max = Datuum
        self.sum1 += Datuum
        self.sum2 += Datuum * Datuum
        
    cpdef long GetN(self):
        return self.N
    
    cpdef double GetMin(self):
        return self.min

    cpdef double GetMax(self):
        return self.max
    
    cpdef double GetDelta(self):
        return self.max - self.min
    
    cpdef double GetAverage(self):
        if self.N > 0:
            return self.sum1 / self.N
        else:
            return 0.0
        
    cpdef double GetVariance(self):
        if self.N > 1:
            avg = self.GetAverage()
            arg = self.sum2 - self.N * avg * avg
            return arg / (self.N - 1)
        # To-DO: check how to properly handle cases when N is not > 1
        else:
            return 1
        
    cpdef double GetStdDev(self):
        return sqrt(self.GetVariance())

            
cdef class DataVector:

    def __init__(self):
        cdef int i
        for i in range(100):
            self.data[i] = Data()
        
    cpdef void Clear(self):
        cdef int i
        # Initialize data objects
        # TO-DO: Check this is working right
        for i in range(100):
            self.data[i] = Data()
        
    cpdef double L2StdDev(self):
        cdef double sum1 = 0.0
        cdef int i

        for i in range(100):
            sum1 += self.data[i].GetVariance()
        
        return sqrt(sum1)
    
    cpdef double LinfStdDev(self):
        cdef double max_val = 0.0
        cdef double var
        cdef int i 
        
        for i in range(100):
            var = self.data[i].GetVariance()
            if var > max_val:
                max_val = var
                
        return sqrt(max_val)