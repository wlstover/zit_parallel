# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zero-Intelligence Traders (ZIT) parallel market simulation. Benchmarks multi-threaded trading performance comparing pure Python and Cython implementations on free-threaded Python (no GIL). Both versions live in one repo under separate subdirectories.

## Build & Run

Requires free-threaded Python (3.13t+). Both versions run from the project root via unified entry point:

```bash
# Run pure Python version
python run.py --mode python

# Build and run Cython version
cd src/cy && python setup.py build_ext --inplace && cd ../..
python run.py --mode cython
```

Analysis notebook: `zit_parallel_analysis.ipynb` (reads `python_trading_log.csv` and `cython_trading_log.csv`)

## Architecture

```
src/
├── py/          # Pure Python implementation
│   ├── main.py  — Model, Agent classes + run_model() entry point
│   ├── data.py  — Data, DataVector statistics classes
│   ├── rng.py   — RandomNumberGenerator (LCG)
│   └── gil_test.py — standalone GIL/threading test utility
├── cy/          # Cython implementation (mirrors py/ structure)
│   ├── main.pyx/pxd — cdef Model, Agent + run_model()
│   ├── data.pyx/pxd — cdef Data, DataVector
│   ├── rng.pyx/pxd  — cdef RandomNumberGenerator
│   └── setup.py     — Cython build config
run.py           # Unified entry point (--mode python|cython)
```

**Data flow**: `run.py` → `run_model()` → creates `Model` with N buyers/sellers → `DoTrading()` spawns threads → each thread runs `DoTrades()` with its own RNG instance on a disjoint slice of agents → lock-protected updates to shared `PriceData`/`TradeData` → results logged to timestamped CSV.

## Key Design Details

- **Thread safety**: Each thread operates on non-overlapping agent slices. Shared `PriceData`/`TradeData` protected by `priceLock`/`tradeLock` context managers
- **Deterministic RNG**: Each thread gets its own LCG seeded with `base_seed + threadNumber`
- **Simulation grid**: Market sizes (10K, 100K, 1M trader pairs) × thread counts (1, then 10–500 step 10)
- **Free-threading**: Cython files declare `# cython: freethreading_compatible=True`
- **Output**: Timestamped `trading_log_YYYYMMDD_HHMMSS.csv` with columns: Threads, Buyers, Sellers, WallTime, CPUtime, NumberOfTrades, QuantityTraded, AveragePrice, StdDev

## Dependencies

Cython (for cy/ build), pandas, numpy, matplotlib (for notebook analysis).
