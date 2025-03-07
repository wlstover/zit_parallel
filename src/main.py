import rng
import time
import data
import threading

import sys
import sysconfig
import logging

seed = 1
seedRandomWithTime = True

if seedRandomWithTime:
    theSeed = time.time()
else:
    theSeed = seed

buyer = True
seller = False

maxBuyerValue = 20
maxSellerValue = 20


class Model:
    
    def __init__(self, numberOfBuyers, numberOfSellers, numThreads):
        
        self.buyers = [Agent(buyer) for i in range(numberOfBuyers)]
        self.sellers = [Agent(seller) for i in range(numberOfSellers)]
        self.numThreads = numThreads
    
        self.priceLock = threading.Lock()
        self.tradeLock = threading.Lock()
        self.TradeData = data.Data()
        self.PriceData = data.Data()
        
        self.threads = []
        self.maxNumberOfTrades = 10 * numberOfBuyers
        
        self.agentsPerThread = numberOfBuyers / numThreads
        self.tradersPerThread = self.maxNumberOfTrades / numThreads

        
    def DoTrades(self, threadNumber):
        
        localRNG = rng.RandomNumberBenerator(theSeed+threadNumber) 
        
        # if self.numThreads <= 10:
        #     print(f'Thread {threadNumber} up and running')
        
        lowerBuyerBound = threadNumber * self.agentsPerThread
        upperBuyerBound = (threadNumber + 1) * self.agentsPerThread - 1
        lowerSellerBound = threadNumber * self.agentsPerThread
        upperSellerBound = (threadNumber + 1) * self.agentsPerThread - 1

        for i in range(1, int(self.tradersPerThread)):
   
            buyerIndex = localRNG.IntegerInRange(lowerBuyerBound, upperBuyerBound)
            bidPrice = self.buyers[buyerIndex].FormBidPrice(localRNG)

            sellerIndex = localRNG.IntegerInRange(lowerSellerBound, upperSellerBound)
            askPrice = self.sellers[sellerIndex].FormAskPrice(localRNG)
            
            # print(f'Buyer {buyerIndex} bids {bidPrice} and holds {self.buyers[buyerIndex].GetQuantityHeld()} units')
            # print(f'Seller {sellerIndex} asks {askPrice} and has {self.sellers[sellerIndex].GetQuantityHeld()} units in stock')
        
            
            if ((self.buyers[buyerIndex].GetQuantityHeld() == 0)
                and (self.sellers[sellerIndex].GetQuantityHeld() == 1)
                and bidPrice >= askPrice):
                
                transactionPrice = localRNG.IntegerInRange(askPrice, bidPrice)

                # print(f'{self.buyers[buyerIndex]} accepts contract at {bidPrice}')
                # print(f'{self.sellers[sellerIndex]} accepts contract at {transactionPrice}')

                self.buyers[buyerIndex].SetPrice(transactionPrice)
                self.sellers[sellerIndex].SetPrice(transactionPrice)
                self.priceLock.acquire()
                self.PriceData.AddDatum(transactionPrice)
                self.priceLock.release()
                
                self.buyers[buyerIndex].SetQuantityHeld(1)
                self.sellers[sellerIndex].SetQuantityHeld(0)
                
                self.tradeLock.acquire()
                self.TradeData.AddDatum(1)
                self.tradeLock.release()
            
        # print([buyer.GetPrice() for buyer in self.buyers])
        
    
    def DoTrading(self, deltaTime1, deltaTime2):
        
        start_time_1 = time.time()
        start_time_2 = time.process_time()
 
        for i in range(self.numThreads):
            thread = threading.Thread(target=self.DoTrades, args=(i,))
            self.threads.append(thread)
            thread.start()
            
        for thread in self.threads:
            thread.join()
            
        end_time1 = time.time()
        end_time2 = time.process_time()
        
        self.delta_time1 = end_time1 - start_time_1
        self.delta_time2 = end_time2 - start_time_2

RNG = rng.RandomNumberBenerator(theSeed)

class Agent:
    def __init__(self, agentType):
        self.buyerOrSeller = agentType
        self.quantityHeld = 0 if agentType == buyer else 1
        self.value = RNG.IntegerInRange(1, maxBuyerValue) if agentType == buyer else RNG.IntegerInRange(1, maxSellerValue)
        self.price = 0
        
    def GetBuyerOrSeller(self):
        return self.buyerOrSeller
    
    def GetQuantityHeld(self):
        return self.quantityHeld
        
    def SetQuantityHeld(self, q):
        self.quantityHeld = q
    
    def FormBidPrice(self, anRNG):
        return anRNG.IntegerInRange(1, self.value)
    
    def FormAskPrice(self, anRNG):
        return anRNG.IntegerInRange(self.value, maxBuyerValue)
        
    def GetPrice(self):
        return self.price
        
    def SetPrice(self, price):
        self.price = price
        
if __name__ == '__main__':

    print(f"Version of python: {sys.version}")
    active = sysconfig.get_config_vars().get("Py_GIL_DISABLED")

    if active is None:
        print("GIL cannot be disabled")
    if active == 0:
        print("GIL is active")
    if active == 1:
        print("GIL is disabled")

    wallTime = 0
    CPUtime = 0
    
    print("ZERO INTELLIGENCE TRADERS\n")
    
    # Configure logging
    logging.basicConfig(filename='trading_log.csv', level=logging.INFO, format='%(message)s')
    logging.info('Threads,Buyers,Sellers,WallTime,CPUtime,NumberOfTrades,QuantityTraded,AveragePrice,StdDev')

    for trader_no in [10000, 100000, 1000000]:
        print(f'Running {trader_no} size market...')
        for i in [1] + list(range(10, 501, 10)):
            # for j in range(1,6):
            numberOfThreads = i
            numberOfBuyers = trader_no
            numberOfSellers = trader_no
                    
            ZITraders = Model(numberOfBuyers, numberOfSellers, numberOfThreads)
            ZITraders.DoTrading(wallTime, CPUtime)
            
            # print(f"Wall-clock time: {ZITraders.delta_time1:.2f} seconds")
            # print(f"CPU time: {ZITraders.delta_time2:.2f} seconds")

            numberOfTrades = numberOfBuyers + numberOfSellers
            quantityTraded = ZITraders.TradeData.GetN()
            averagePrice = ZITraders.PriceData.GetAverage()
            stdDev = ZITraders.PriceData.GetStdDev()

            # Log the results
            # print(f"Ran {numberOfThreads} threads in {ZITraders.delta_time1} seconds")
            logging.info(f'{numberOfThreads},{numberOfBuyers},{numberOfSellers},{ZITraders.delta_time1:.2f},{ZITraders.delta_time2:.2f},{numberOfTrades},{quantityTraded},{averagePrice},{stdDev}')
            
        print(f'....Done')
            # print(f'Number of trades = {numberOfTrades}')
            # print(f'Quantity traded = {quantityTraded}')
            # print(f'The average price = {averagePrice} and the s.d. is {stdDev}')
    
    print(f'ZIT MODEL COMPLETE')