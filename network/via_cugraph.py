import os
import cudf
import cugraph as cg


class ViaCuGraph:

    def __init__(self,  edge_list_path: os.PathLike):
        self.edge_list_path = edge_list_path
        self.reinitialize()
        self.half_edges = list(self.g.edges())[0::2]
        self.half_nodes = list(self.g.nodes())[0::2]

    def reinitialize(self):
        # https://docs.rapids.ai/api/cugraph/stable/
        df = cudf.read_csv(self.edge_list_path, sep=' ', header=None,
                           dtype=['int64', 'int64'])
        self.g = cg.Graph()
        self.g.from_cudf_edgelist(df, source='0', destination='1')

    def parse(self):
        self.reinitialize()

    def pagerank(self):
        # https://docs.rapids.ai/api/cugraph/stable/api_docs/api/cugraph.link_analysis.pagerank.pagerank.html?highlight=pagerank
        return cg.pagerank(self.g)

    def community(self):
        # https://docs.rapids.ai/api/cugraph/stable/api_docs/api/cugraph.community.louvain.louvain.html?highlight=louvain#cugraph.community.louvain.louvain
        return cg.louvain(self.g)

    def wcc(self):
        # https://docs.rapids.ai/api/cugraph/stable/api_docs/api/cugraph.components.connectivity.weakly_connected_components.html?highlight=weakly_connected_components#cugraph.components.connectivity.weakly_connected_components
        return cg.components.connectivity.weakly_connected_components(self.g)

    def force_layout(self):
        # https://docs.rapids.ai/api/cugraph/stable/api_docs/api/cugraph.layout.force_atlas2.force_atlas2.html?highlight=force_atlas2
        return cg.force_atlas2(self.g)

    def pairwise_distances(self):
        raise NotImplementedError()

    def close(self):
        self.g = None
