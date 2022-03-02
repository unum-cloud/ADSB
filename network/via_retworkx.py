import pandas as pd
import retworkx as rx


class ViaRetworkX:

    def __init__(self, df: pd.DataFrame):
        # https://retworkx.readthedocs.io/en/latest/stubs/retworkx.PyDiGraph.html
        self.g = rx.PyDiGraph().extend_from_weighted_edge_list(
            [tuple(x) for _, x in df.iterrows()])

    def pagerank(self):
        raise NotImplementedError()

    def community(self):
        raise NotImplementedError()

    def wcc(self):
        return rx.weakly_connected_components(self.g)

    def force_layout(self):
        return rx.spring_layout(self.g)

    def pairwise_distances(self):
        return rx.digraph_floyd_warshall(self.g)

    def close(self):
        self.g = None