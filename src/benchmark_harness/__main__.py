import argparse
import importlib
from typing import Callable

from .runner import run


def load_target(specification: str) -> Callable[[], object]:
    try:
        module_name, attribute = specification.split(":", maxsplit=1)
    except ValueError as error:
        raise ValueError("target must use module:function syntax") from error
    target = getattr(importlib.import_module(module_name), attribute)
    if not callable(target):
        raise TypeError("target must be callable")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark a zero-argument Python callable")
    parser.add_argument("target", help="module:function")
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=10)
    args = parser.parse_args()
    result = run(
        load_target(args.target),
        warmups=args.warmups,
        iterations=args.iterations,
    )
    print(result.to_json())


if __name__ == "__main__":
    main()

