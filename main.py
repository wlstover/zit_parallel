import random as rnd
import rng
import time
import data
import threading

seed = 1
seedRandomWithTime = True

if seedRandomWithTime:
    theSeed = time.time()
else:
    theSeed = seed

buyer = True
seller = False

maxNumberOfTrades = 10000

numberOfBuyers = 10
numberOfSellers = 10

maxBuyerValue = 20
maxSellerValue = 20

numThreads = 1
agentsPerThread = numberOfBuyers / numThreads
tradersPerThread = maxNumberOfTrades / numThreads


class Model:
    
    def __init__(self, numberOfBuyers, numberOfSellers):
        self.buyers = [Agent(buyer) for i in range(numberOfBuyers)]
        self.sellers = [Agent(seller) for i in range(numberOfSellers)]
    
        self.priceLock = None
        self.tradeLock = None
        self.TradeData = data.Data()
        self.PriceData = data.Data()
        
        self.threads = []
        
    def DoTrades(self, threadNumber):
        
        localRNG = rng.RandomNumberBenerator(theSeed+threadNumber) 
        
        if numThreads <= 10:
            print(f'Thread {threadNumber} up and running')
        
        lowerBuyerBound = threadNumber * agentsPerThread
        upperBuyerBound = (threadNumber + 1) * agentsPerThread - 1
        lowerSellerBound = threadNumber * agentsPerThread
        upperSellerBound = (threadNumber + 1) * agentsPerThread - 1
        
        for i in range(1, int(tradersPerThread)):
            # CHECK THIS - int float problems
            buyerIndex = int(rnd.uniform(lowerBuyerBound, upperBuyerBound))
            bidPrice = self.buyers[buyerIndex].FormBidPrice(localRNG)
        
        for i in range(1, int(tradersPerThread)):
            sellerIndex = int(rnd.uniform(lowerSellerBound, upperSellerBound))
            askPrice = self.sellers[sellerIndex].FormAskPrice(localRNG)
            
        print(f'Buyer {buyerIndex} bids {bidPrice} and holds {self.buyers[buyerIndex].GetQuantityHeld()} units')
        print(f'Seller {sellerIndex} asks {askPrice} and has {self.sellers[sellerIndex].GetQuantityHeld()} units in stock')
       
        
        if ((self.buyers[buyerIndex].GetQuantityHeld == 0)
            and (self.sellers[sellerIndex].GetQuantityHeld() == 1)
            and bidPrice >= askPrice):
            
            transactionPrice = localRNG.IntegerInRange(askPrice, bidPrice)
            self.buyers[buyerIndex].SetPrice(transactionPrice)
            self.sellers[sellerIndex].SetPrice(transactionPrice)
            #priceLock.lock()
            self.PriceData.AddDatum(transactionPrice)
            #priceLock.unlock()
            
            self.buyers[buyerIndex].SetQuantityHeld(1)
            self.sellers[sellerIndex].SetQuantityHeld(0)
            
            #tradeLock.lock()
            self.TradeData.AddDatum(1)
            #tradeLock.unlock()
            
        
    
    def DoTrading(self, deltaTime1, deltaTime2):
        
        start_time_1 = time.time()
        start_time_2 = time.process_time()
 
        for i in range(numThreads):
            thread = threading.Thread(target=self.DoTrades, args=(i,))
            self.threads.append(thread)
            thread.start()
            
        for thread in self.threads:
            thread.join()
            
        end_time1 = time.time()
        end_time2 = time.process_time()
        
        delta_time1 = end_time1 - start_time_1
        delta_time2 = end_time2 - start_time_2
        
        print(f"Wall-clock time: {delta_time1:.2f} seconds")
        print(f"CPU time: {delta_time2:.2f} seconds")


class Agent:
    def __init__(self, agentType):
        self.buyerOrSeller = agentType
        self.quantityHeld = [0 if buyer else 1]
        self.value = rnd.uniform(1, maxBuyerValue) if agentType == 'buyer' else rnd.uniform(1, maxSellerValue)
        self.price = 0
        
    def GetBuyerOrSeller(self):
        return self.buyerOrSeller
    
    def GetQuantityHeld(self):
        return self.quantityHeld
        
    def SetQuantityHeld(self, q):
        self.quantityHeld = q
    
    def FormBidPrice(self, rng):
        return rnd.uniform(1, self.value)
    
    def FormAskPrice(self, rng):
        return rnd.uniform(self.value, maxBuyerValue)
        
    def GetPrice(self):
        return self.price
        
    def SetPrice(self, price):
        self.price = price
        
if __name__ == '__main__':
    wallTime = 0
    CPUtime = 0
    
    print("ZERO INTELLIGENCE TRADERS")
    
    ZITraders = Model(numberOfBuyers, numberOfSellers)
    
    ZITraders.DoTrading(wallTime, CPUtime)
    
    # print(f'The model took {wallTime} seconds to execute using {CPUtime/CLOCKS_PER_SEC} seconds on the cores')
    print(f'Number of trades = {numberOfBuyers + numberOfSellers}')
    print(f'Quantity traded = {ZITraders.TradeData.GetN()}')
    print(f'The average price = {ZITraders.PriceData.GetAverage()} and the s.d. is {ZITraders.PriceData.GetStdDev()}')
    