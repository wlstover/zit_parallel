# main.pyx
# cython: freethreading_compatible=True

from data cimport Data, DataVector
import time
import threading
from rng cimport RandomNumberGenerator
import rng
import logging
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime

MAX_THREADS = 500

cdef RandomNumberGenerator RNG

seed = 1
seedRandomWithTime = True

if seedRandomWithTime:
    theSeed = time.time()
else:
    theSeed = seed

RNG = rng.RandomNumberGenerator(theSeed)

buyer = True
seller = False

maxBuyerValue = 20
maxSellerValue = 20


cdef class Model:

    cdef public int numberOfBuyers
    cdef public int numberOfSellers
    cdef public int numThreads
    cdef public int agentsPerThread
    cdef public int tradersPerThread
    cdef public int maxNumberOfTrades
    cdef public list buyers
    cdef public list sellers
    cdef public object priceLock
    cdef public object tradeLock
    cdef public Data PriceData
    cdef public Data TradeData
    cdef public double delta_time1
    cdef public double delta_time2

    def __init__(self, numberOfBuyers, numberOfSellers, numThreads):

        self.buyers = [Agent(buyer) for i in range(numberOfBuyers)]
        self.sellers = [Agent(seller) for i in range(numberOfSellers)]
        self.numThreads = numThreads

        self.priceLock = threading.Lock()
        self.tradeLock = threading.Lock()
        self.TradeData = Data()
        self.PriceData = Data()

        self.maxNumberOfTrades = 10 * numberOfBuyers

        self.agentsPerThread = numberOfBuyers / numThreads
        self.tradersPerThread = self.maxNumberOfTrades / numThreads


    def DoTrades(self, threadNumber, localBuyers, localSellers):

        cdef RandomNumberGenerator localRNG
        localRNG = rng.RandomNumberGenerator(theSeed+threadNumber)

        cdef long buyerIndex, sellerIndex, bidPrice, askPrice, transactionPrice
        cdef long numLocalAgents
        cdef int i

        numLocalAgents = len(localBuyers)

        localPriceData = Data()
        localTradeData = Data()

        for i in range(1, int(self.tradersPerThread)):

            buyerIndex = localRNG.IntegerInRange(0, numLocalAgents - 1)
            bidPrice = localBuyers[buyerIndex].FormBidPrice(localRNG)

            sellerIndex = localRNG.IntegerInRange(0, numLocalAgents - 1)
            askPrice = localSellers[sellerIndex].FormAskPrice(localRNG)

            if ((localBuyers[buyerIndex].GetQuantityHeld() == 0)
                and (localSellers[sellerIndex].GetQuantityHeld() == 1)
                and bidPrice >= askPrice):

                transactionPrice = localRNG.IntegerInRange(askPrice, bidPrice)

                localBuyers[buyerIndex].SetPrice(transactionPrice)
                localSellers[sellerIndex].SetPrice(transactionPrice)
                localPriceData.AddDatum(transactionPrice)

                localBuyers[buyerIndex].SetQuantityHeld(1)
                localSellers[sellerIndex].SetQuantityHeld(0)

                localTradeData.AddDatum(1)

        with self.priceLock:
            self.PriceData.Merge(localPriceData)
        with self.tradeLock:
            self.TradeData.Merge(localTradeData)


    def DoTrading(self, deltaTime1, deltaTime2, executor):

        start_time_1 = time.time()
        start_time_2 = time.process_time()

        futures = []
        for i in range(self.numThreads):
            lo = i * self.agentsPerThread
            hi = (i + 1) * self.agentsPerThread
            localBuyers = self.buyers[lo:hi]
            localSellers = self.sellers[lo:hi]
            futures.append(executor.submit(self.DoTrades, i, localBuyers, localSellers))

        for f in futures:
            f.result()

        end_time1 = time.time()
        end_time2 = time.process_time()

        self.delta_time1 = end_time1 - start_time_1
        self.delta_time2 = end_time2 - start_time_2


cdef class Agent:

    cdef public int index
    cdef public int quantityHeld
    cdef public double price
    cdef public double value
    cdef public bint buyerOrSeller

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

def _warm_pool(executor, n):
    barrier = threading.Barrier(n)
    futures = [executor.submit(barrier.wait) for _ in range(n)]
    wait(futures)


def run_model():
    wallTime = 0
    CPUtime = 0

    print("ZERO INTELLIGENCE TRADERS\n")

    # Configure logging
    log_filename = f'trading_log_cython_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(message)s', force=True)
    logging.info('Threads,Buyers,Sellers,WallTime,CPUtime,NumberOfTrades,QuantityTraded,AveragePrice,StdDev')

    executor = ThreadPoolExecutor(max_workers=MAX_THREADS)
    _warm_pool(executor, MAX_THREADS)

    for trader_no in [10000, 100000, 1000000]:
        print(f'Running {trader_no} size market...')
        for i in [1, 2, 5] + list(range(10, 501, 10)):
            numberOfThreads = i
            numberOfBuyers = trader_no
            numberOfSellers = trader_no

            ZITraders = Model(numberOfBuyers, numberOfSellers, numberOfThreads)
            ZITraders.DoTrading(wallTime, CPUtime, executor)

            numberOfTrades = numberOfBuyers + numberOfSellers
            quantityTraded = ZITraders.TradeData.GetN()
            averagePrice = ZITraders.PriceData.GetAverage()
            stdDev = ZITraders.PriceData.GetStdDev()

            logging.info(f'{numberOfThreads},{numberOfBuyers},{numberOfSellers},{ZITraders.delta_time1:.2f},{ZITraders.delta_time2:.2f},{numberOfTrades},{quantityTraded},{averagePrice},{stdDev}')

        print(f'....Done')

    executor.shutdown()
    print(f'ZIT MODEL COMPLETE')

if __name__ == '__main__':
    run_model()
