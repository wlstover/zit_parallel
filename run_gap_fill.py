"""Run only the missing thread counts (2, 5) and append to existing CSVs."""
import sys
import os
import csv
import time

MISSING_THREADS = [2, 5]
MARKET_SIZES = [10000, 100000, 1000000]

def run_gap(mode):
    if mode == 'python':
        from src.py.main import Model
        output_csv = 'python_trading_log.csv'
    elif mode == 'cython':
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'cy'))
        from main import Model
        output_csv = 'cython_trading_log.csv'
    else:
        raise ValueError(f"Unknown mode: {mode}")

    print(f"Filling gaps for {mode} implementation -> {output_csv}")

    with open(output_csv, 'a', newline='') as f:
        writer = csv.writer(f)

        for trader_no in MARKET_SIZES:
            for num_threads in MISSING_THREADS:
                print(f"  {trader_no} traders x {num_threads} threads...", end=' ', flush=True)

                m = Model(trader_no, trader_no, num_threads)
                m.DoTrading(0, 0)

                numberOfTrades = trader_no * 2
                quantityTraded = m.TradeData.GetN()
                averagePrice = m.PriceData.GetAverage()
                stdDev = m.PriceData.GetStdDev()

                writer.writerow([
                    num_threads, trader_no, trader_no,
                    f'{m.delta_time1:.2f}', f'{m.delta_time2:.2f}',
                    numberOfTrades, quantityTraded, averagePrice, stdDev
                ])
                f.flush()
                print(f"done ({m.delta_time1:.2f}s)")

    print(f"Appended to {output_csv}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['python', 'cython', 'both'], default='both')
    args = parser.parse_args()

    modes = ['python', 'cython'] if args.mode == 'both' else [args.mode]
    for mode in modes:
        run_gap(mode)

    print("Gap fill complete.")
