from dataclasses import asdict, dataclass
import json
from statistics import fmean, median
from time import perf_counter_ns
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class BenchmarkResult:
    warmups: int
    iterations: int
    samples_ns: tuple[int, ...]
    minimum_ns: int
    median_ns: float
    mean_ns: float
    maximum_ns: int

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def run(
    operation: Callable[[], T],
    *,
    warmups: int = 3,
    iterations: int = 10,
    clock: Callable[[], int] = perf_counter_ns,
) -> BenchmarkResult:
    if warmups < 0:
        raise ValueError("warmups must be non-negative")
    if iterations < 1:
        raise ValueError("iterations must be positive")

    for _ in range(warmups):
        operation()

    samples: list[int] = []
    for _ in range(iterations):
        started = clock()
        operation()
        elapsed = clock() - started
        if elapsed < 0:
            raise ValueError("clock must be monotonic")
        samples.append(elapsed)

    return BenchmarkResult(
        warmups=warmups,
        iterations=iterations,
        samples_ns=tuple(samples),
        minimum_ns=min(samples),
        median_ns=median(samples),
        mean_ns=fmean(samples),
        maximum_ns=max(samples),
    )

