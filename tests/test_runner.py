import json
import unittest

from benchmark_harness import run


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


if __name__ == "__main__":
    unittest.main()
