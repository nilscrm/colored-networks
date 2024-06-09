from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx


type Node = int
type Color = str


@dataclass
class Edge:
    v1: Node
    v2: Node
    color: Color


@dataclass
class Rule:
    input: dict[Color, int]
    new_edges: list[Edge]
    internal_rewiring: dict[Color, list[tuple[Node, Color]]]
    external_rewiring: dict[tuple[Color, Color], Color]


class ColoredGraph:
    def __init__(self, rules: list[Rule] = [], edges: list[Edge] = []):
        self.rules = rules
        self.edges = edges
        self.free_node_id = max([edge.v1 for edge in edges] + [edge.v2 for edge in edges], default=-1) + 1

    def new_node(self) -> Node:
        self.free_node_id += 1
        return self.free_node_id
    
    def reduce(self, verbose=False):
        if verbose:
            self.draw()
        while self.reduce_all_nodes(verbose):
            pass
    
    def reduce_all_nodes(self, verbose=False) -> bool:
        reduced_any = False
        for node in set([edge.v1 for edge in self.edges] + [edge.v2 for edge in self.edges]):
            did_reduce = self.reduce_node(node, verbose)
            reduced_any = reduced_any or did_reduce
        return reduced_any

    def reduce_node(self, node: Node, verbose=True) -> bool:
        node_edges = [edge for edge in self.edges if edge.v1 == node or edge.v2 == node]
        color_counts = {}
        for edge in node_edges:
            color_counts[edge.color] = color_counts.get(edge.color, 0) + 1

        for i, rule in enumerate(self.rules):
            if rule.input == color_counts:
                if verbose:
                    print(f'Applying rule {i}')
                # remove old edges
                for edge in node_edges:
                    self.edges.remove(edge)

                neighbors = [(edge.v2 if edge.v1 == node else edge.v1, edge.color) for edge in node_edges]

                # External rewiring
                for n1, color1 in neighbors:
                    for n2, color2 in neighbors:
                        if n1 != n2 and (color1, color2) in rule.external_rewiring:
                            self.edges.append(Edge(n1, n2, rule.external_rewiring[(color1, color2)]))

                # Create new node for each node to not have duplicate names
                node_name_mapping = {}
                for edge in rule.new_edges:
                    if edge.v1 not in node_name_mapping:
                        node_name_mapping[edge.v1] = self.new_node()
                    if edge.v2 not in node_name_mapping:
                        node_name_mapping[edge.v2] = self.new_node()
                    self.edges.append(Edge(node_name_mapping[edge.v1], node_name_mapping[edge.v2], edge.color))

                # Internal rewiring
                for edge in node_edges:
                    neighbor = edge.v2 if edge.v1 == node else edge.v1
                    for rewired_node in rule.internal_rewiring.get(edge.color, []):
                        self.edges.append(Edge(neighbor, node_name_mapping[rewired_node], edge.color))

                if verbose:
                    self.draw()
            
                # Only apply one rule
                return True
        return False

    def draw(self):
        G = nx.Graph()
        for edge in self.edges:
            G.add_edge(edge.v1, edge.v2, color=edge.color)
        edge_colors = [G[u][v]['color'] for u, v in G.edges()]
        nx.draw(G, with_labels=True, edge_color=edge_colors)
        plt.show()
