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

Pass a `setup` callable when every iteration needs fresh state. Setup runs
before warmups and measured iterations but remains outside the timed interval.

For operations close to the timer's practical resolution, set
`operations_per_sample` to measure a batch and inspect
`samples_ns_per_operation` for normalized values. Setup still runs once per
sample, not once per operation, so batching is only appropriate when every
operation in a batch can share the prepared state. Raw batch durations remain
available in `samples_ns`.

Run tests with `python -m unittest discover -s tests`.

Zero-argument callables can also be benchmarked from the command line:

```bash
PYTHONPATH=src python3 -m benchmark_harness package.module:function --warmups 3 --iterations 20
```

The CLI accepts `--operations-per-sample` for the same batching behavior.
