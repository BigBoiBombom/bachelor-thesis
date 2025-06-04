import pandas as pd
import networkx as nx
import community as community_louvain
import igraph as ig
import leidenalg

input_csv = "hostux_social-edges.csv"
nodes_csv = "hostux_social-nodes.csv"

data = pd.read_csv(input_csv, header=None, names=["source", "target"])
G = nx.from_pandas_edgelist(data, source="source", target="target", create_using=nx.DiGraph())

def label_propagation(G):
    communities = nx.algorithms.community.label_propagation.label_propagation_communities(G.to_undirected())
    return {node: i for i, comm in enumerate(communities) for node in comm}

def louvain(G):
    return community_louvain.best_partition(G.to_undirected())

def leiden(G):
    edges = list(G.edges())
    g_igraph = ig.Graph(directed=True)
    g_igraph.add_vertices(list(set(G.nodes())))
    g_igraph.add_edges(edges)
    partition = leidenalg.find_partition(g_igraph, leidenalg.ModularityVertexPartition)
    result = {}
    for i, community in enumerate(partition):
        for node in community:
            result[g_igraph.vs[node]["name"]] = i
    return result

label_prop_communities = label_propagation(G)
louvain_communities = louvain(G)
leiden_communities = leiden(G)

nodes_data = pd.read_csv(nodes_csv)
nodes_data["label_prop"] = nodes_data["name"].map(label_prop_communities).fillna(-1).astype(int)
nodes_data["louvain"] = nodes_data["name"].map(louvain_communities).fillna(-1).astype(int)
nodes_data["leiden"] = nodes_data["name"].map(leiden_communities).fillna(-1).astype(int)

nodes_data.to_csv(nodes_csv, index=False)

print(f"Updated '{nodes_csv}' with community columns: 'label_prop', 'louvain', 'leiden'.")
