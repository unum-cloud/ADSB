import retworkx as rx


class ReDiGraph:

    def from_edgelist(self, df):
        self.graph = rx.PyDiGraph()
        self.graph.extend_from_weighted_edge_list(
            [tuple(x) for x in df.to_records(index=False)])

    def pagerank(self):
        return

    def wcc(self):
        return rx.weakly_connected_components(self.graph)

    def floyd_warshall(self):
        return rx.digraph_floyd_warshall(self.graph)

    def community(self):
        return

    def force_layout(self):
        return rx.spring_layout(self.graph)