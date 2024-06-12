from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx
from typing import Self


type Color = str


@dataclass(eq=True, frozen=True)
class Node:
    id: int
    label: str = ""


@dataclass
class Edge:
    v1: Node
    v2: Node
    color: Color


@dataclass
class Rule:
    name: str | None
    input: dict[Color, int]
    new_edges: list[Edge]
    internal_rewiring: dict[Color, list[tuple[Node, Color]]]
    external_rewiring: dict[tuple[Color, Color], Color]


# TODO: Maybe allow singleton nodes
class ColoredNetwork:
    def __init__(self, rules: list[Rule] = [], edges: list[Edge] = []):
        self.rules = rules
        self.edges = edges
        self.free_node_id = max([edge.v1.id for edge in edges] + [edge.v2.id for edge in edges], default=-1) + 1

    def new_node(self, label: str = "") -> Node:
        self.free_node_id += 1
        return Node(self.free_node_id, label)

    def reduce(self, verbose=False):
        while self.reduce_all_nodes(verbose):
            pass
        if verbose:
            self.draw()

    def reduce_all_nodes(self, verbose=False) -> bool:
        reduced_any = False
        for node in set([edge.v1 for edge in self.edges] + [edge.v2 for edge in self.edges]):
            did_reduce = self.reduce_node(node, verbose)
            reduced_any = reduced_any or did_reduce
        return reduced_any

    def reduce_node(self, node: Node, verbose=True) -> bool:
        node_edges = [edge for edge in self.edges if edge.v1.id == node.id or edge.v2.id == node.id]
        color_counts = {}
        for edge in node_edges:
            color_counts[edge.color] = color_counts.get(edge.color, 0) + 1

        for rule in self.rules:
            if rule.input == color_counts:
                if verbose:
                    self.draw(mark_red=node)
                    print(f"Applying rule '{rule.name}' to node {node}")
                # remove old edges
                for edge in node_edges:
                    self.edges.remove(edge)

                neighbors = [(edge.v2 if edge.v1.id == node.id else edge.v1, edge.color) for edge in node_edges]

                # External rewiring
                for n1, color1 in neighbors:
                    for n2, color2 in neighbors:
                        if n1.id != n2.id and (color1, color2) in rule.external_rewiring:
                            # This if is to prevent two edges appearning for rules that connect the same colors
                            if color1 == color2 and n1.id < n2.id:
                                continue
                            self.edges.append(Edge(n1, n2, rule.external_rewiring[(color1, color2)]))

                # Add new edges
                node_name_mapping = {}
                for edge in rule.new_edges:
                    if edge.v1.id not in node_name_mapping:
                        node_name_mapping[edge.v1.id] = self.new_node(label=edge.v1.label)
                    if edge.v2.id not in node_name_mapping:
                        node_name_mapping[edge.v2.id] = self.new_node(label=edge.v2.label)
                    self.edges.append(Edge(node_name_mapping[edge.v1.id], node_name_mapping[edge.v2.id], edge.color))

                # Internal rewiring
                for edge in node_edges:
                    neighbor = edge.v2 if edge.v1.id == node.id else edge.v1
                    for rewired_node, new_color in rule.internal_rewiring.get(edge.color, []):
                        if rewired_node.id not in node_name_mapping:
                            node_name_mapping[rewired_node.id] = self.new_node(label=rewired_node.label)
                        self.edges.append(Edge(neighbor, node_name_mapping[rewired_node.id], new_color))

                # Only apply one rule
                return True
        return False

    def draw(self, mark_red: Node | None = None):
        G = nx.Graph()
        vertex_lables = {}
        for edge in self.edges:
            G.add_edge(edge.v1.id, edge.v2.id, color=edge.color)
            vertex_lables[edge.v1.id] = edge.v1.label
            vertex_lables[edge.v2.id] = edge.v2.label
        edge_colors = [G[u][v]["color"] for u, v in G.edges()]
        node_colors = [
            "lightcoral" if mark_red is not None and node == mark_red.id else "skyblue" for node in G.nodes()
        ]
        nx.draw(G, labels=vertex_lables, node_color=node_colors, edge_color=edge_colors)
        plt.show()

    def seems_isomorphic_to(self, other: Self) -> bool:
        nodes1 = set([edge.v1.id for edge in self.edges] + [edge.v2.id for edge in self.edges])
        nodes2 = set([edge.v1.id for edge in other.edges] + [edge.v2.id for edge in other.edges])

        colors1 = sorted(
            [sorted(edge.color for edge in self.edges if edge.v1.id == node or edge.v2.id == node) for node in nodes1]
        )
        colors2 = sorted(
            [sorted(edge.color for edge in other.edges if edge.v1.id == node or edge.v2.id == node) for node in nodes2]
        )

        return colors1 == colors2
