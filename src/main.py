import logging       


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