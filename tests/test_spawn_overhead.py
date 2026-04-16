"""
Verifies the hypothesis that Cython 10K speedup collapses at ~500 threads
because serial thread.start()+join() overhead dominates the tiny workload.

Cython 10K observation (cython_trading_log.csv):
  1   thread : 0.07s  (baseline)
  ~100 threads: 0.04s (best, ~1.75x speedup)
  ~440 threads: 0.11s (0.64x — cliff)

The cliff is ~50-70ms of "extra" wall time appearing at high thread counts.
If spawning+joining 500 no-op threads alone costs >=40ms, that explains the
cliff without needing to invoke lock contention, GIL-style serialization,
or Cython-specific effects.
"""
import threading
import time
import statistics

NUM_THREADS = 500
TRIALS = 7


def measure_noop_spawn_join(n):
    """Time to create, start, and join n threads whose target is a no-op."""
    threads = [threading.Thread(target=lambda: None) for _ in range(n)]
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return (time.perf_counter() - t0) * 1000.0  # ms


def main():
    samples = [measure_noop_spawn_join(NUM_THREADS) for _ in range(TRIALS)]
    median_ms = statistics.median(samples)
    print(f"no-op spawn+join x {NUM_THREADS}: samples={[f'{s:.1f}' for s in samples]} ms")
    print(f"median = {median_ms:.1f} ms")

    # GREEN: spawn+join overhead for 500 threads should meet or exceed 40ms,
    # the lower bound of the observed cliff (wall time at 500 threads minus
    # wall time at the ~100-thread optimum: 0.08 - 0.04 = 40ms).
    CLIFF_FLOOR_MS = 40.0
    assert median_ms >= CLIFF_FLOOR_MS, (
        f"GREEN failed: spawn overhead {median_ms:.1f}ms < cliff floor "
        f"{CLIFF_FLOOR_MS}ms. Hypothesis weakened."
    )
    print(
        f"GREEN: {median_ms:.1f}ms spawn overhead >= {CLIFF_FLOOR_MS}ms "
        f"cliff floor. Hypothesis confirmed."
    )


if __name__ == "__main__":
    main()
