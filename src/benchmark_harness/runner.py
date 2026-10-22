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
    median_absolute_deviation_ns: float
    mean_ns: float
    maximum_ns: int

    @property
    def samples_ns_per_operation(self) -> tuple[float, ...]:
        return tuple(
            sample / self.operations_per_sample for sample in self.samples_ns
        )

    @property
    def median_ns_per_operation(self) -> float:
        return self.median_ns / self.operations_per_sample

    @property
    def mean_ns_per_operation(self) -> float:
        return self.mean_ns / self.operations_per_sample

    @property
    def median_absolute_deviation_ns_per_operation(self) -> float:
        return self.median_absolute_deviation_ns / self.operations_per_sample

    @property
    def relative_median_absolute_deviation(self) -> Optional[float]:
        if self.median_ns == 0:
            return None
        return self.median_absolute_deviation_ns / self.median_ns

    @property
    def operations_per_second(self) -> Optional[float]:
        if self.mean_ns_per_operation == 0:
            return None
        return 1_000_000_000 / self.mean_ns_per_operation

    def to_json(self) -> str:
        payload = asdict(self)
        payload.update(
            samples_ns_per_operation=self.samples_ns_per_operation,
            median_ns_per_operation=self.median_ns_per_operation,
            mean_ns_per_operation=self.mean_ns_per_operation,
            median_absolute_deviation_ns_per_operation=(
                self.median_absolute_deviation_ns_per_operation
            ),
            relative_median_absolute_deviation=(
                self.relative_median_absolute_deviation
            ),
            operations_per_second=self.operations_per_second,
        )
        return json.dumps(payload, indent=2)


def run(
    operation: Callable[[], T],
    *,
    warmups: int = 3,
    iterations: int = 10,
    operations_per_sample: int = 1,
    setup: Optional[Callable[[], None]] = None,
    teardown: Optional[Callable[[], None]] = None,
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
        try:
            for _ in range(operations_per_sample):
                operation()
        finally:
            if teardown is not None:
                teardown()

    samples: list[int] = []
    for _ in range(iterations):
        if setup is not None:
            setup()
        try:
            started = clock()
            for _ in range(operations_per_sample):
                operation()
            elapsed = clock() - started
        finally:
            if teardown is not None:
                teardown()
        if elapsed < 0:
            raise ValueError("clock must be monotonic")
        samples.append(elapsed)

    sample_median = median(samples)
    return BenchmarkResult(
        warmups=warmups,
        iterations=iterations,
        operations_per_sample=operations_per_sample,
        samples_ns=tuple(samples),
        minimum_ns=min(samples),
        median_ns=sample_median,
        median_absolute_deviation_ns=median(
            abs(sample - sample_median) for sample in samples
        ),
        mean_ns=fmean(samples),
        maximum_ns=max(samples),
    )
