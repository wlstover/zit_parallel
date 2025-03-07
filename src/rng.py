from libc.stdint cimport INT_MAX

cdef class RandomNumberGenerator:
    cdef long last

    def __init__(self, long seed):
        self.last = seed

    cdef long LongInteger(self):
        cdef long k = self.last // 127773
        self.last = 16807 * (self.last - k * 127773) - k * 2836
        if self.last < 0:
            self.last += INT_MAX
        return self.last

    cpdef int IntegerInRange(self, int min, int max):
        return min + self.LongInteger() % (max - min + 1)

    cpdef double UnitReal(self):
        return self.LongInteger() * (1.0 / INT_MAX)

    cpdef double RealInRange(self, double min, double max):
        return min + (max - min) * self.UnitReal()

    cpdef Test(self, double LowerLimit, double UpperLimit, int SizeOfTest, str WhatToTest, int ExtentOfOutput):
        cdef double sum1 = 0
        cdef double sum2 = 0
        cdef long theIntegerNumber
        cdef double theRealNumber
        cdef double avg, variance

        if WhatToTest == 'LongInteger':
            for i in range(SizeOfTest):
                theIntegerNumber = self.LongInteger()
                sum1 += theIntegerNumber
                sum2 += theIntegerNumber * theIntegerNumber
                if ExtentOfOutput == 2:
                    print(theIntegerNumber)

        elif WhatToTest == 'IntegerInRange':
            for i in range(SizeOfTest):
                theIntegerNumber = self.IntegerInRange(int(LowerLimit), int(UpperLimit))
                sum1 += theIntegerNumber
                sum2 += theIntegerNumber * theIntegerNumber
                if ExtentOfOutput == 2:
                    print(theIntegerNumber)

        elif WhatToTest == 'UnitReal':
            for i in range(SizeOfTest):
                theRealNumber = self.UnitReal()
                sum1 += theRealNumber
                sum2 += theRealNumber * theRealNumber
                if ExtentOfOutput == 2:
                    print(theRealNumber)

        elif WhatToTest == 'RealInRange':
            for i in range(SizeOfTest):
                theRealNumber = self.RealInRange(LowerLimit, UpperLimit)
                sum1 += theRealNumber
                sum2 += theRealNumber * theRealNumber
                if ExtentOfOutput == 2:
                    print(theRealNumber)

        avg = sum1 / SizeOfTest
        if SizeOfTest != 1:
            variance = (sum2 - sum1 * sum1 / SizeOfTest) / (SizeOfTest - 1)

        if ExtentOfOutput >= 1:
            print(f'Average should be: {LowerLimit + (UpperLimit - LowerLimit) / 2.0}; actual: {avg}')
            if SizeOfTest != 1:
                print(f'Variance should be: {(UpperLimit - LowerLimit) ** 2 / 12}; actual: {variance}')
