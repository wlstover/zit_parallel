"""Smoke test: 10K-pair run on a warmed pool should not show the 500-thread cliff."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "cy"))
import main as sim  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

import statistics  # noqa: E402

TRIALS = 5

executor = ThreadPoolExecutor(max_workers=500)
sim._warm_pool(executor, 500)

print(f"{'threads':>8} {'median(s)':>10} {'samples(s)':>40}")
for n_threads in [1, 100, 440, 500]:
    samples = []
    for _ in range(TRIALS):
        m = sim.Model(10000, 10000, n_threads)
        m.DoTrading(0, 0, executor)
        samples.append(m.delta_time1)
    med = statistics.median(samples)
    sample_str = "[" + ", ".join(f"{s:.3f}" for s in samples) + "]"
    print(f"{n_threads:>8} {med:>10.3f} {sample_str:>40}")

executor.shutdown()
