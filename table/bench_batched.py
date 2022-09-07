
from typing import List, Generator


from via_any_batched import ViaAnyBatched
from shared import Sample, load_persisted_benchmarks, list_contains_benchmark, persist_benchmarks, measure_time
import dataset

files_per_batch: int = 2
results_path = __file__.rsplit('.', 1)[0] + '.json'
persisted_samples = load_persisted_benchmarks(results_path)
paths = dataset.parquet_paths()


def run_backend(
    class_: type,
    class_name: str,
) -> List[Sample]:

    logic_engine = class_()
    engine = ViaAnyBatched(
        logic_engine, files_per_batch) if files_per_batch != 0 else logic_engine

    names = ['Load', 'Q1', 'Q2', 'Q3', 'Q4']
    funcs = [lambda: engine.load(
        paths), engine.query1, engine.query2, engine.query3, engine.query4]
    samples = []

    print('Starting engine:', class_name)
    for name, func in zip(names, funcs):

        sample = Sample(
            iterations=1,
            operation=name,
            backend=class_name,
            dataset='Taxi Rides',
            dataset_bytes=int(39e9),
        )

        if list_contains_benchmark(persisted_samples, sample):
            continue

        try:
            sample.seconds = measure_time(func)
            samples.append(sample)
        except Exception as e:
            print(e)

    engine.close()
    return samples


def run_backends(backend_names: List[str]) -> Generator[Sample, None, None]:

    if 'Pandas' in backend_names:
        from via_pandas import ViaPandas
        yield from run_backend(ViaPandas, 'Pandas')

    if 'PyArrow' in backend_names:
        from via_arrow import ViaArrow
        yield from run_backend(ViaArrow, 'PyArrow')

    if 'Modin' in backend_names:
        from via_modin import ViaModin
        yield from run_backend(ViaModin, 'Modin')

    if 'CuDF' in backend_names:
        from via_cudf import ViaCuDF
        yield from run_backend(ViaCuDF, 'CuDF')

    if 'SQLite' in backend_names:
        from via_sqlite import ViaSQLite
        yield from run_backend(ViaSQLite, 'SQLite')

    if 'Dask->CuDF' in backend_names:
        from via_dask_cudf import ViaDaskCuDF
        yield from run_backend(ViaDaskCuDF, 'Dask->CuDF')

    if 'Dask+CuDF' in backend_names:
        from via_dask_cudf import ViaDaskCuDFUnified
        yield from run_backend(ViaDaskCuDFUnified, 'Dask+CuDF')

    if 'PySpark' in backend_names:
        from via_spark import ViaPySpark
        yield from run_backend(ViaPySpark, 'PySpark')


if __name__ == '__main__':

    try:
        for sample in run_backends([
            'Pandas',
            'PyArrow',
            # 'Modin',
            # 'CuDF',
            # 'SQLite',
            # 'PySpark',
            # 'Dask->CuDF',
            # 'Dask+CuDF',
        ]):
            persisted_samples.append(sample)
    except KeyboardInterrupt:
        pass

    persist_benchmarks(persisted_samples, results_path)
