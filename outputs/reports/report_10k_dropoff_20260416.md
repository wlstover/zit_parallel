# ZIT Parallel: 10K Cython drop-off investigation and fix

Date: 2026-04-16
Machine: 11th-gen Intel i5-1135G7, 4 physical cores / 8 logical (SMT)
Runtime: free-threaded CPython 3.13.13t

## TL;DR

The dramatic drop-off on the 10K-pair Cython line (speedup collapsing from ~1.75x to ~0.65x past 200 threads in the prior run) was an artifact of per-run `threading.Thread` creation overhead, not of lock contention, GIL behavior, or anything Cython-specific. Replacing the per-run thread spawn with a reused `ThreadPoolExecutor` that is warmed once before the benchmark grid eliminated the cliff entirely: at 10K the wall time is now flat at ~0.03s across every thread count from 1 to 500.

Regression at large thread counts has not disappeared and should not disappear — it is genuine Amdahl's-law behavior shaped by the machine's core topology, and it is expected to reappear on any future run. What the fix removed was a measurement artifact sitting on top of the real physics.

## What was changed

1. `src/py/main.py` and `src/cy/main.pyx`:
   - Replaced the per-run `threading.Thread(target=...).start() / .join()` loop in `Model.DoTrading` with submission to a `concurrent.futures.ThreadPoolExecutor` passed in from `run_model`.
   - Removed the now-unused `self.threads` list (and its `cdef public list threads` declaration on the Cython side).
   - Fixed a latent `/` → `//` integer-division bug in `src/py/main.py`'s `agentsPerThread` / `tradersPerThread` computations. This never triggered in Cython because `cdef public int` coerced floats to ints, but under pure Python the float slice indices raised `TypeError` the first time the pooled code path was exercised.

2. `run_model` in both implementations now:
   - Creates a single `ThreadPoolExecutor(max_workers=500)` before the benchmark grid.
   - Warms the pool via a `threading.Barrier(500)` so all 500 worker threads exist concurrently before any timed run begins.
   - Reuses that pool for every `(market_size, numThreads)` configuration and shuts it down at the end.

3. Logs are now mode-prefixed and timestamped (`trading_log_python_YYYYMMDD_HHMMSS.csv`, `trading_log_cython_YYYYMMDD_HHMMSS.csv`) so runs never overwrite each other and the two implementations' outputs remain unambiguous.

4. `generate_plots.py` takes explicit `--python` and `--cython` CSV paths and writes timestamped figures (`zit_parallel_{mode}_YYYYMMDD_HHMMSS.png`).

5. Two diagnostic scripts were added under `tests/`:
   - `test_spawn_overhead.py`: a red/green verification test that times no-op thread spawn+join at N=500 and asserts the measured overhead is at least the size of the observed wall-time cliff.
   - `test_pool_smoke.py`: runs 10K pairs at 1, 100, 440, and 500 threads with a warmed pool and reports medians.

## The story behind the drop-off

### What the cliff actually looked like

Prior Cython 10K walltimes (one trial per thread count):

| Threads | Wall (s) | Speedup |
|---|---|---|
| 1   | 0.07 | 1.00 |
| 10  | 0.05 | 1.40 |
| 100 | 0.04 | 1.75 (peak) |
| 200 | 0.05 | 1.40 |
| 400 | 0.09 | 0.78 |
| 440 | 0.11 | 0.64 (worst) |
| 500 | 0.08 | 0.88 |

The 100K-pair and 1M-pair lines plateaued in roughly the same absolute shape; the 10K line dove below 1.0x.

### Why only 10K

Every run of `DoTrading` paid a cost proportional to the requested number of threads: 500 sequential `threading.Thread(...).start()` calls, each performing a `clone(2)` syscall and allocating a thread stack. On this machine the measured cost of spawning and joining 500 no-op threads has a median of ~63 ms (see `tests/test_spawn_overhead.py`, which confirmed the hypothesis via a red/green assertion).

That 63 ms is a fixed overhead that does not shrink as the workload shrinks. At 10K pairs, the entire serial computation takes about 70 ms of useful work. Adding 63 ms of pure spawn cost on top nearly doubles wall time; the ratio becomes a 0.64x "speedup." At 100K pairs the work is 10x larger, so the same 63 ms is a minor tax. At 1M pairs it is negligible. This is why the cliff was visible only on the 10K line.

Pure Python did not show the cliff because its 1-thread baseline is roughly 0.80 s — eleven times slower than Cython's 0.07 s — so the 63 ms spawn cost is noise against its workload even at 500 threads.

### Confirming the hypothesis

The diagnostic in `tests/test_spawn_overhead.py` times 500 no-op `threading.Thread` spawn+join cycles and asserts the median meets or exceeds 40 ms (the lower bound of the observed cliff = wall_time@500 − wall_time@optimum = 0.08 − 0.04). The RED phase of the TDD cycle inverted the assertion (overhead < 5 ms, the "negligible" null hypothesis) and observed 62.8 ms, failing with the exact magnitude needed to explain the cliff. The GREEN phase, with the assertion restored to its hypothesis form, passes at 63.6 ms.

## Why the cliff is no longer a problem

With a reused, pre-warmed pool, `DoTrading` no longer creates any threads. It only dispatches work via `executor.submit`, which is a queue push plus a condvar wake — microseconds rather than ~100 µs per thread. The 63 ms tax is paid once, before timing begins, and amortized across the entire benchmark grid.

New Cython 10K walltimes (post-fix):

| Threads | Wall (s) | Speedup |
|---|---|---|
| 1   | 0.03 | 1.00 |
| 100 | 0.03 | 1.04 |
| 440 | 0.03 | 1.00 |
| 500 | 0.03 | 0.94 |

The line is flat. The 10K workload still does not benefit from parallelism (it is too small to amortize even the intra-run coordination cost), but it no longer actively regresses. The speedup curve now honestly reports what the hardware can and cannot do for a 100,000-iteration workload, rather than conflating that with a fixed-cost measurement artifact.

This reframes the paper narrative cleanly: parallelism helps above ~100K agents on this machine; below that, the work is simply too small for threading to pay off. That is a defensible, hardware-independent statement. The prior figure obscured it with a large, language-independent overhead artifact.

## Why regression at scale is still expected

Removing the spawn-cost artifact does not — and should not — make regression disappear. The remaining shape is the real physics of Amdahl's law on a small shared-memory machine, and it will recur on any future run:

### On the current laptop (4 physical / 8 logical cores)

Cython 1M walltimes show a clear peak-then-plateau:

| Threads | Wall (s) | Speedup | CPU/wall |
|---|---|---|---|
| 1  | 7.24 | 1.00 | 1.00 |
| 2  | 4.55 | 1.59 | 1.98 |
| 5  | 3.33 | 2.17 (peak) | 4.63 |
| 10 | 3.60 | 2.01 | 6.68 |
| 20 | 5.04 | 1.44 | 7.37 |
| 30+ | ~4.9 | ~1.48 | ~7.2 |

The minimum wall time lands at 5 threads (one past the physical core count), not at 8 threads (the logical count). SMT does not help this workload: Cython's tight typed inner loop has few memory or branch stalls for a hyperthread sibling to hide under. Pure Python on the same machine bottoms out at 10 threads (near the logical count) because its looser per-iteration code leaves the stalls SMT needs.

Once past the physical-core sweet spot, total CPU time inflates faster than linearly (5.1x at 20 threads vs 20x the threads), reflecting coordination overhead — atomic refcount contention on shared class/method objects under free-threading, scheduler switches, cache-line ping-pong. Wall time rises accordingly from 3.33 s back up to ~5.0 s.

### On the 16-core target machine

The same physics will produce a shifted curve:

- Expected Cython 1M peak at **threads ≈ physical cores** (≈16 on a 16-core box, likely observed at 12–16 based on the C++11 figure in the paper).
- Expected Python 1M peak at **threads ≈ logical cores** (≈16 with SMT off, ≈32 with SMT on).
- Regression past those peaks is expected and matches prior results in the paper — specifically the C++11 threads figure (peak at 10–15 on 16 cores), Scala's 100K line, Haskell's small/medium problems, and Clojure across all sizes.

### Why this is the story the paper wants

The paper's Summary already names this finding: *"Sometimes this optimal level is clearly related to hardware considerations, when the best number of threads is approximately the number of cores present."* Our Cython 1M peak at 5 threads (≈4 physical cores) is a textbook instance. Rather than a flaw to excuse, the hardware-shaped peak is evidence that free-threaded Python now behaves like the compiled languages surveyed in the paper — real parallel scaling with hardware-bounded peaks — instead of like Fig. 9's GIL-bound Python, which sat below 1.0 speedup at every thread count.

The practical implication for future runs: when the 16-core run lands, regression past ~16 threads is the expected and desired result. It should be reported, not tuned away. The invariant the fix guarantees is that the regression observed reflects Amdahl's law plus hardware topology, not thread-library startup cost.
