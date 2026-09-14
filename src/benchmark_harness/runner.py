from dataclasses import asdict, dataclass
import json
from statistics import fmean, median
from time import perf_counter_ns
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class BenchmarkResult:
    warmups: int
    iterations: int
    operations_per_sample: int
    samples_ns: tuple[int, ...]
    minimum_ns: int
    median_ns: float
    mean_ns: float
    maximum_ns: int

    @property
    def samples_ns_per_operation(self) -> tuple[float, ...]:
        return tuple(
            sample / self.operations_per_sample for sample in self.samples_ns
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def run(
    operation: Callable[[], T],
    *,
    warmups: int = 3,
    iterations: int = 10,
    operations_per_sample: int = 1,
    setup: Optional[Callable[[], None]] = None,
    clock: Callable[[], int] = perf_counter_ns,
) -> BenchmarkResult:
    if warmups < 0:
        raise ValueError("warmups must be non-negative")
    if iterations < 1:
        raise ValueError("iterations must be positive")
    if operations_per_sample < 1:
        raise ValueError("operations_per_sample must be positive")

    for _ in range(warmups):
        if setup is not None:
            setup()
        for _ in range(operations_per_sample):
            operation()

    samples: list[int] = []
    for _ in range(iterations):
        if setup is not None:
            setup()
        started = clock()
        for _ in range(operations_per_sample):
            operation()
        elapsed = clock() - started
        if elapsed < 0:
            raise ValueError("clock must be monotonic")
        samples.append(elapsed)

    return BenchmarkResult(
        warmups=warmups,
        iterations=iterations,
        operations_per_sample=operations_per_sample,
        samples_ns=tuple(samples),
        minimum_ns=min(samples),
        median_ns=median(samples),
        mean_ns=fmean(samples),
        maximum_ns=max(samples),
    )
