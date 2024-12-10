INT_MAX = 2147483647

class RandomNumberBenerator:
    def __init__(self, seed):
        self.last = seed
    
    def LongInteger(self):
        k = self.last / 127773
        self.last = 16807 * (self.last - k   * 127773) - k * 2836
        if self.last < 0:
            self.last += INT_MAX
            
    def IntegerInRange(self, min, max):
        return min + self.LongInteger() % (max - min + 1)
    
    def UnitReal(self):
        return float(self.LongInteger() / float(INT_MAX))
    
    def RealInRange(self, min, max):
        return min + (max - min) * self.UnitReal()
    
    def Test(self, LowerLimit, UpperLimit, SizeOfTest, WhatToTest, ExtentOfOutput):
        sum1 = 0
        sum2 = 0
        
        if type(WhatToTest) == 'LongInteger':
            for i in range(SizeOfTest):
                theIntegerNumber = self.LongInteger()
                sum1 += theIntegerNumber
                sum2 += theIntegerNumber * theIntegerNumber
                if ExtentOfOutput == 2:
                    print(theIntegerNumber)
            
            LowerLimit = 1
            UpperLimit = INT_MAX - 1
                
        elif type(WhatToTest) == 'LongIntegerInRange':
            for i in range(SizeOfTest):
                theIntegerNumber = self.IntegerInRange(LowerLimit, UpperLimit)
                sum1 += theIntegerNumber
                sum2 += theIntegerNumber * theIntegerNumber
                if (ExtentOfOutput == 2):
                    print(theIntegerNumber)
                    
        elif type(WhatToTest) == 'UnitReal':
            for i in range(SizeOfTest):
                theRealNumber = self.UnitReal()
                sum1 += theRealNumber
                sum2 += theRealNumber * theRealNumber
                if (ExtentOfOutput == 2):
                    print(theRealNumber)
                
                LowerLimit = 0
                UpperLimit = 1
                
        elif type(WhatToTest) == 'RealInRange':
            for i in range(SizeOfTest):
                theRealNumber = self.RealInRange(LowerLimit, UpperLimit)
                sum1 += theRealNumber
                sum2 += theRealNumber * theRealNumber
                if ExtentOfOutput == 2:
                    print(theRealNumber)
        
        avg = sum1 / SizeOfTest
        if SizeOfTest != 1:
            variance = (sum2 - sum1 * sum1 / SizeOfTest)/(SizeOfTest - 1)
            
        if ExtentOfOutput >= 1:
            print(f'Average should be: {LowerLimit + (UpperLimit - LowerLimit) / 2.0}; actual: {avg}')
            if SizeOfTest != 1:
                print(f'Variance should be: {(UpperLimit-LowerLimit)**2 / 12}; actual: {variance}')
            