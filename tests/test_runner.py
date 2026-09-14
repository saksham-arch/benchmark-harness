import json
import unittest

from benchmark_harness import run
from benchmark_harness.__main__ import load_target


class FakeClock:
    def __init__(self, values: list[int]) -> None:
        self._values = iter(values)

    def __call__(self) -> int:
        return next(self._values)


class RunnerTests(unittest.TestCase):
    def test_runs_warmups_and_records_samples(self) -> None:
        calls = 0

        def operation() -> None:
            nonlocal calls
            calls += 1

        result = run(
            operation,
            warmups=2,
            iterations=3,
            clock=FakeClock([0, 10, 20, 35, 50, 80]),
        )
        self.assertEqual(calls, 5)
        self.assertEqual(result.samples_ns, (10, 15, 30))
        self.assertEqual(result.median_ns, 15)
        self.assertEqual(json.loads(result.to_json())["iterations"], 3)

    def test_validates_configuration(self) -> None:
        with self.assertRaises(ValueError):
            run(lambda: None, warmups=-1)
        with self.assertRaises(ValueError):
            run(lambda: None, iterations=0)
        with self.assertRaises(ValueError):
            run(lambda: None, operations_per_sample=0)

    def test_loads_callable_target(self) -> None:
        target = load_target("json:loads")
        self.assertTrue(callable(target))

    def test_rejects_invalid_target_specification(self) -> None:
        with self.assertRaises(ValueError):
            load_target("missing_separator")

    def test_runs_setup_before_each_iteration_outside_timing(self) -> None:
        events: list[str] = []

        def setup() -> None:
            events.append("setup")

        def operation() -> None:
            events.append("operation")

        result = run(
            operation,
            warmups=1,
            iterations=2,
            setup=setup,
            clock=FakeClock([0, 5, 10, 15]),
        )
        self.assertEqual(
            events,
            ["setup", "operation", "setup", "operation", "setup", "operation"],
        )
        self.assertEqual(result.samples_ns, (5, 5))

    def test_batches_short_operations_and_reports_normalized_samples(self) -> None:
        calls = 0

        def operation() -> None:
            nonlocal calls
            calls += 1

        result = run(
            operation,
            warmups=1,
            iterations=2,
            operations_per_sample=4,
            clock=FakeClock([0, 20, 30, 42]),
        )

        self.assertEqual(calls, 12)
        self.assertEqual(result.operations_per_sample, 4)
        self.assertEqual(result.samples_ns, (20, 12))
        self.assertEqual(result.samples_ns_per_operation, (5.0, 3.0))
        self.assertEqual(json.loads(result.to_json())["operations_per_sample"], 4)


if __name__ == "__main__":
    unittest.main()
