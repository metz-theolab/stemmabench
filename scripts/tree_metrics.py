import sys


import networkx as nx
import numpy as np
from itertools import combinations

class TreeMetrics:
    def __init__(self, file_target, file_rebuild):
        """
        Initializes a TreeMetrics object.

        :param file_target: Path to the file containing the edges of the target tree.
        :type file_target: str
        :param file_rebuild: Path to the file containing the edges of the rebuilt tree.
        :type file_rebuild: str
        """
        self.file_target = file_target
        self.file_rebuild = file_rebuild
        self.Tree_target = self.graph_from_edges(file_target)
        self.Tree_rebuild = self.graph_from_edges(file_rebuild)

    def sign(self, x):
        """
        Returns the sign of a number.

        :param x: The number.
        :type x: int or float
        :return: The sign of the number (-1, 0, or 1).
        :rtype: int
        """
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0

    def u(self, A, B, C):
        """
        Calculates the u value for a triplet of nodes.

        :param A: First node.
        :type A: str
        :param B: Second node.
        :type B: str
        :param C: Third node.
        :type C: str
        :return: The u value.
        :rtype: float
        """
        cal = 1 - 0.5 * abs(
            self.sign((len(nx.shortest_path(self.Tree_rebuild, A, B)) - 1) - (len(nx.shortest_path(self.Tree_rebuild, A, C)) - 1)) -
            self.sign((len(nx.shortest_path(self.Tree_target, A, B)) - 1) - (len(nx.shortest_path(self.Tree_target, A, C)) - 1))
        )
        return cal

    def Roos_similarity(self):
        """
        Calculates the Roos similarity metric for the target and rebuilt trees.

        :return: The Roos similarity metric.
        :rtype: float
        """
        similarity = 0
        labels = list(self.Tree_target.nodes())
        triplets = list(combinations(labels, 3))
        for i in range(len(triplets)):
            A = triplets[i][0]
            B = triplets[i][1]
            C = triplets[i][2]
            similarity += self.u(A, B, C)

        return similarity

    def graph_edit_distance(self, times=120):
        """
        Calculates the graph edit distance between the target and rebuilt trees.

        :param times: The maximum time in seconds to compute the graph edit distance. Default is 120 seconds.
        :type times: int
        :return: The graph edit distance between the target and rebuilt trees.
        :rtype: float
        """
        return nx.graph_edit_distance(self.Tree_target, self.Tree_rebuild, timeout=times)

    def save_graph(self, graph, path):
        """
        Saves a graph to a file.

        :param graph: The graph to save.
        :type graph: nx.Graph
        :param path: The path to save the graph.
        :type path: str
        """
        nx.write_gexf(graph, path)

    @staticmethod
    def graph_from_edges(path_to_edges):
        """
        Creates a graph from a list of edges.

        :param edges: Path to the file containing the edges of the graph.
        :type edges: str
        :return: The graph created from the edges.
        :rtype: nx.Graph
        """
        G = nx.DiGraph()
        edges_file = open(path_to_edges, "r")
        clear = edges_file.readlines()
        for i in range(len(clear)):
            clear[i] = clear[i].replace("\n", "").replace("\"(", "").replace("\'", "").replace(")", "").replace("(", "").replace(" ", "")
            clear[i] = clear[i].split(",")
            if clear[i][0] not in list(G.nodes()):
                G.add_node(clear[i][0])
            if clear[i][1] not in list(G.nodes()):
                G.add_node(clear[i][1])
            G.add_edge(clear[i][0], clear[i][1], weight=1)
            G.add_edge(clear[i][1], clear[i][0], weight=1)
        return G

    @staticmethod
    def build_distance_matrix(tree: nx.DiGraph):
        """
        Builds a distance matrix from a tree.

        :param tree: The tree to build the distance matrix from.
        :type tree: nx.DiGraph
        :return: The distance matrix.
        :rtype: list
        """
        nodes = list(tree.nodes())
        matrix = np.zeros((len(nodes), len(nodes)))
        for i, node1 in enumerate(nodes):
            for j, node2 in enumerate(nodes):
                if j >= i:
                    matrix[i][j] = nx.shortest_path_length(tree, node1, node2)
        return matrix + matrix.T

def main():
    if len(sys.argv) != 4:
        print("Usage: python tree_metrics.py <file_target> <file_rebuild> <output_file>")
        sys.exit(1)

    file_target = sys.argv[1]
    file_rebuild = sys.argv[2]
    output_file = sys.argv[3]

    tree_metrics = TreeMetrics(file_target, file_rebuild)

    roos_similarity = tree_metrics.Roos_similarity()
    graph_edit_distance = tree_metrics.graph_edit_distance()

    with open(output_file, 'w') as f:
        f.write(f"Roos et al : {roos_similarity}\n")
        f.write(f"Graph edit : {graph_edit_distance}\n")

if __name__ == "__main__":
    main()