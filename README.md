# benchmark-harness

A minimal Python benchmark runner with explicit warmup and measured phases.
It reports raw samples alongside summary statistics so results remain
inspectable.

Results include median absolute deviation (MAD) alongside minimum, median,
mean, and maximum duration. MAD is the median distance from the sample median,
so one extreme sample has less influence than it would on standard deviation.
`relative_median_absolute_deviation` divides MAD by the median so dispersion can
be compared across different duration scales; it is `null` when the median is
zero. A low relative or absolute MAD does not establish a stable environment:
retain the raw samples and inspect the full range and experimental conditions.

```python
from benchmark_harness import run

result = run(lambda: sum(range(1000)), warmups=3, iterations=20)
print(result.to_json())
```

This harness measures wall-clock duration with `time.perf_counter_ns`. It does
not control CPU frequency, process affinity, or background load; document those
conditions before treating comparisons as evidence.

`pause_seconds` waits between measured samples, after teardown and outside the
timed interval. It does not pause after the final sample or between warmups.
The pause can reduce back-to-back load, but it does not guarantee a particular
temperature, clock frequency, or independent samples. The CLI exposes the same
option as `--pause-seconds`.

Pass a `setup` callable when every iteration needs fresh state. Setup runs
before warmups and measured iterations but remains outside the timed interval.
Pass a `teardown` callable to release per-sample resources after every warmup
and measured sample. Teardown also remains outside timing and runs in a
`finally` block when the operation raises. Setup and teardown each run once per
sample, not once per operation in a batch.

For operations close to the timer's practical resolution, set
`operations_per_sample` to measure a batch and inspect
`samples_ns_per_operation` for normalized values. Setup still runs once per
sample, not once per operation, so batching is only appropriate when every
operation in a batch can share the prepared state. Raw batch durations remain
available in `samples_ns`. JSON output includes both the raw samples and derived
per-operation samples, median, and mean; normalization divides each batch by
its configured operation count and does not remove measurement overhead. The
normalized output also includes MAD per operation.

The nearest-rank `p95_ns` retains a slower observed batch duration, and
`p95_ns_per_operation` divides that batch by the configured operation count.
With few samples p95 is coarse; normalized values still include loop and timer
overhead and do not describe a single isolated invocation.

JSON output reports `operations_per_second`, derived from the mean normalized
duration. It is `null` when the measured mean is zero. This is the reciprocal
rate of sequential work inside this process; it is not concurrent throughput,
capacity under load, or a production service claim. Timer overhead and batching
assumptions remain part of the measurement.

Run tests with `PYTHONPATH=src python3 -m unittest discover -s tests`.

Zero-argument callables can also be benchmarked from the command line:

```bash
PYTHONPATH=src python3 -m benchmark_harness package.module:function --warmups 3 --iterations 20
```

The CLI accepts `--operations-per-sample` for the same batching behavior.
