# benchmark-harness

A minimal Python benchmark runner with explicit warmup and measured phases.
It reports raw samples alongside summary statistics so results remain
inspectable.

```python
from benchmark_harness import run

result = run(lambda: sum(range(1000)), warmups=3, iterations=20)
print(result.to_json())
```

This harness measures wall-clock duration with `time.perf_counter_ns`. It does
not control CPU frequency, process affinity, or background load; document those
conditions before treating comparisons as evidence.

Run tests with `python -m unittest discover -s tests`.

