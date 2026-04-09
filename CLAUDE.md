# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zero-Intelligence Traders (ZIT) parallel market simulation. Benchmarks multi-threaded trading performance comparing Python and Cython implementations. Agents randomly generate bids/asks and trade when conditions are met, with results logged to CSV for analysis.

## Build & Run

All source lives in `src/`. Commands must be run from that directory:

```bash
# Compile Cython extensions (requires Cython installed)
cd src && python setup.py build_ext --inplace

# Run the simulation
cd src && python runner.py
```

Analysis notebook: `zit_parallel_analysis.ipynb`

Profiler utility: `python profiler.py` (converts .prof to CSV)

## Architecture

**Entry point**: `runner.py` → calls `main.run_model()`

**Core modules** (all Cython `.pyx` with `.pxd` headers):
- `main.pyx` — `Model` class (market setup, threaded trading), `Agent` class (buyers/sellers), `run_model()` iterates over market sizes × thread counts
- `data.pyx` — `Data` (running statistics) and `DataVector` (collection of 100 Data objects with norm calculations) for tracking prices and trade counts
- `rng.pyx` — Linear congruential generator. Each thread gets its own RNG instance seeded with `base_seed + threadNumber` for deterministic, thread-safe randomness

**Supporting files**:
- `constants.py` — path configuration (`ROOT_DIR`, `OUTPUTS_DIR`, `FIGURES_DIR`)
- `profiler.py` — converts pstats `.prof` output to `profile_results.csv`

## Key Design Details

- **Thread safety**: Lock-protected updates to shared `PriceData` and `TradeData` via `priceLock`/`tradeLock`
- **Simulation grid**: Market sizes (10K, 100K, 1M trader pairs) × thread counts (1, then 10–500 step 10)
- **Trade logic**: Buyer bids RNG(1, value), seller asks RNG(value, 20). Trade executes when buyer has 0 units, seller has 1 unit, and bid ≥ ask. Transaction price = RNG(ask, bid)
- **Output**: `trading_log.csv` with columns: Threads, Buyers, Sellers, WallTime, CPUtime, NumberOfTrades, QuantityTraded, AveragePrice, StdDev

## Dependencies

Cython, pandas, numpy, matplotlib (for notebook analysis). Python stdlib: threading, logging, pstats.
