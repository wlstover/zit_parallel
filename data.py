from math import sqrt

DataVectorSize = 100

class Data:
    def __init__(self):
        self.N = 0 
        self.min = 1000000.0  # 10^6
        self.max = 0.0
        self.sum1 = 0.0
        self.sum2 = 0.0
        
    def AddDatum(self, Datuum):
        N = N + 1
        if Datuum < min:
            min = Datuum
        elif Datuum > max:
            max = Datuum
        self.sum1 += Datuum
        self.sum2 += Datuum * Datuum
        
    def GetN(self):
        return self.N
    
    def GetMin(self):
        return self.min

    def GetMax(self):
        return self.max
    
    def GetDelta(self):
        return self.max - self.min
    
    def GetAverage(self):
        if self.N > 0:
            return self.sum1 / self.N
        else:
            return 0.0
        
    def GetVariance(self):
        if self.N > 1:
            avg = self.GetAverage()
            arg = self.sum2 - self.N * avg * avg
            return arg / (self.N - 1)
        # To-DO: check how to properly handle cases when N is not > 1
        else:
            return 1
        
    def GetStdDev(self):
        return sqrt(self.GetVariance())

            
class DataVector:
    def __init__(self):
        self.data = Data[DataVectorSize]
        
    def Clear(self):
        # Initialize data objects
        # TO-DO: Check this is working right
        for i in range(DataVectorSize):
            self.data[i].__init__()
        
    def L2StdDev(self):
        sum1 = 0.0
        for i in range(DataVectorSize):
            sum1 += self.data[i].GetVariance()
        
        return sqrt(sum1)
    
    def LinfStdDev(self):
        max = 0.0
        
        for i in range(DataVectorSize):
            var = self.data[i].GetVariance()
            if var > max:
                max = var
                
        return sqrt(max)