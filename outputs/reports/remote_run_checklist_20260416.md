# Remote-run checklist: 16-core machine

Date: 2026-04-16
Target: external 16-core terminal (paper-matching hardware)
Source machine: 4-core laptop (where changes were developed)

## Before you leave the laptop

Commit or stash the current working tree so the remote pull is a clean state. Currently uncommitted:

- `src/py/main.py` — pool refactor, `/` → `//` fix
- `src/cy/main.pyx` — pool refactor, removed `self.threads`
- `generate_plots.py` — CLI args, timestamped output filenames
- `tests/test_spawn_overhead.py` (new) — red/green spawn-overhead diagnostic
- `tests/test_pool_smoke.py` (new) — 10K smoke test
- `outputs/reports/report_10k_dropoff_20260416.md` (new) — investigation writeup
- `outputs/reports/remote_run_checklist_20260416.md` (this file)

Also present but unrelated to these changes: untracked CSVs and figures from the laptop run — decide whether to carry those over or leave them as a laptop-local artifact.

## On the 16-core machine

### 1. Interpreter check

Confirm the Python on PATH is a free-threaded 3.13t+ build:

```
python -c "import sys; print(sys.version); print('GIL enabled:', sys._is_gil_enabled())"
```

Expected: version string contains `experimental free-threading build` and `GIL enabled: False`. If not, point at the right interpreter (e.g., a conda env equivalent to this laptop's `nogil` env).

### 2. Dependencies

Install once per environment:

```
pip install cython pandas numpy matplotlib
```

### 3. Rebuild Cython on target

The `.so` files on the laptop are specific to that CPU architecture and Python build — they will not load on the remote box. Rebuild in place:

```
cd src/cy && python setup.py build_ext --inplace && cd ../..
```

Expected: three `.cpython-313t-*.so` files refreshed under `src/cy/`. No errors from `gcc`.

### 4. Smoke test (optional, ~1 second)

Before committing to the ~25-minute full run, verify the pooled code path works end-to-end:

```
python tests/test_pool_smoke.py
```

Expected: a table showing 10K wall times at 1, 100, 440, and 500 threads. All values should be small (single- or low-double-digit milliseconds); no exceptions.

### 5. Full benchmark

Cython first (~5 min on this laptop — likely faster on a 16-core box), then Python (~20 min):

```
python run.py --mode cython
python run.py --mode python
```

Each run writes a mode-prefixed, timestamped CSV into the current directory:

```
trading_log_cython_YYYYMMDD_HHMMSS.csv
trading_log_python_YYYYMMDD_HHMMSS.csv
```

### 6. Generate figures

Pass the two latest CSVs explicitly:

```
latest_py=$(ls -t trading_log_python_*.csv | head -1)
latest_cy=$(ls -t trading_log_cython_*.csv | head -1)
python generate_plots.py --python "$latest_py" --cython "$latest_cy"
```

Output: `outputs/figures/zit_parallel_{python,cython}_YYYYMMDD_HHMMSS.png`.

## What to expect on 16 cores

Based on the analysis in `report_10k_dropoff_20260416.md`:

- **Cython 1M**: peak around threads ≈ 12–16 (near physical core count, mirroring the paper's C++11 figure), mild regression beyond.
- **Python 1M**: peak around threads ≈ logical core count (16 without SMT, 32 with SMT).
- **10K line for both**: flat — no cliff, no significant speedup (workload is too small to benefit from threading regardless of core count).
- **100K line**: intermediate — should scale partway toward the 1M result.

Regression past the peak is the expected, desired finding — it matches the paper's existing narrative that the optimal thread count is hardware-shaped. Do not try to tune it away.

## Quick capture for paper notes

After the run, record the machine details into the CSV or a sibling file so the plots are self-describing:

```
nproc
lscpu | grep -E "^(CPU|Thread|Core|Socket|Model name)"
```

Paste the output next to the generated figures in the paper's figure captions or appendix.
