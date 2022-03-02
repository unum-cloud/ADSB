import os
import time
from dataclasses import dataclass
from typing import Callable, List, Iterable

import pandas as pd

NoneType = type(None)


@dataclass
class Sample:

    # Categorical properties of the benchmark
    backend: str = ''
    operation: str = ''
    dataset: str = ''
    dataset_bytes: int = 0

    # Runtime results
    seconds: float = 0.0
    iterations: int = 0
    error: str = ''

    def __repr__(self) -> str:
        suffix = self.error if len(
            self.error) else f'{self.iterations} iterations'
        return f'{self.backend}.{self.operation}({self.dataset}): {suffix}'


@dataclass
class Bench:

    # Categorical properties of the benchmark
    backend: str
    operation: str
    dataset: str
    dataset_bytes: int

    # Runtime callable
    func: Callable[[], NoneType]

    def __repr__(self) -> str:
        return f'{self.backend}.{self.operation}({self.dataset})'

    def __call__(self, max_seconds: float = 10.0) -> Sample:
        s = Sample()
        s.operation = self.operation
        s.backend = self.backend
        s.dataset = self.dataset
        s.dataset_bytes = self.dataset_bytes

        start = time.time()
        while True:
            try:
                self.func()
            except Exception as e:
                s.error = str(e)
                break

            s.iterations += 1
            s.seconds = time.time() - start
            if s.seconds > max_seconds:
                break

        return s


def list_contains_benchmark(samples: List[Sample], bench: Bench) -> bool:
    for s in samples:
        if s.backend == bench.backend and s.operation == bench.operation and s.dataset == bench.dataset:
            return True
    return False


def find_previous_size(samples: List[Sample], bench: Bench) -> Optional[Sample]:
    last_size = None
    for s in samples:
        if s.backend == bench.backend and s.operation == bench.operation:
            if last_size is None or last_size.dataset_bytes < s.dataset_bytes:
                last_size = s
    return last_size


def run_persisted_benchmarks(
    benchmarks: Iterable[Bench],
    max_seconds: float = 10.0,
    filename: os.PathLike = 'bench.json',
):

    # Retrieve previous results
    samples = []
    if os.path.exists(filename):
        samples = pd.read_json(filename, orient='records')
        samples = [Sample(**s) for _, s in samples.iterrows()]

    # Bench and track results
    try:
        for bench in benchmarks:

            # Skip benchmarks we have already run.
            if list_contains_benchmark(samples, bench):
                print('Skipping:', bench)
                continue

            # Skip benchmarks that will take too long.
            # For that find the biggest dataset processed with
            # this backend and check if it's above our threshold.
            previous = find_previous_size(samples, bench)
            if previous is not None:
                if previous.seconds > max_seconds and previous.iterations == 1:
                    continue

            print('Will run:', bench)
            sample = bench(max_seconds=max_seconds)
            if len(sample.error) == 0:
                samples.append(sample)
                print('-- finished:', sample)

    # If the time run out - gracefully save intermediate results!
    except KeyboardInterrupt:
        pass

    # Format into a table
    samples = [s.__dict__ for s in samples]
    samples = pd.DataFrame(samples)
    samples.to_json(filename, orient='records')