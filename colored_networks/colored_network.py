from dataclasses import dataclass
import matplotlib.pyplot as plt
import networkx as nx
from typing import Self


@dataclass(eq=True, frozen=True)
class Node:
    id: int
    label: str = ""


type Color = str


@dataclass
class Edge:
    v1: Node
    v2: Node
    color: Color


@dataclass
class SplitRule:
    name: str | None
    input: dict[Color, int]
    node1_connection: dict[Color, Color]
    node2_connection: dict[Color, Color]


@dataclass
class DeleteRule:
    name: str | None
    input: dict[Color, int]
    rewiring: dict[tuple[Color, Color], Color]


class ColoredNetwork:
    def __init__(self, nodes: list[Node], edges: list[Edge], rules: list[SplitRule | DeleteRule]):
        self.nodes = nodes
        self.rules = rules
        self.edges = edges
        self.free_node_id = max([node.id for node in nodes], default=-1) + 1

    def new_node(self, label: str = "") -> Node:
        self.free_node_id += 1
        return Node(self.free_node_id, label)

    def reduce(self, verbose=False):
        while self.reduce_all_nodes(verbose):
            pass
        if verbose:
            self.draw()

    def reduce_all_nodes(self, verbose=False) -> bool:
        return any(self.reduce_node(node, verbose) for node in self.nodes)

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
                # delte node
                self.nodes.remove(node)

                neighbors = [(edge.v2 if edge.v1.id == node.id else edge.v1, edge.color) for edge in node_edges]

                match rule:
                    case SplitRule():
                        # Add two new nodes with their connections
                        node1 = self.new_node(label=node.label)
                        node2 = self.new_node(label=node.label)
                        self.nodes.append(node1)
                        self.nodes.append(node2)
                        for neighbor, color in neighbors:
                            if color in rule.node1_connection:
                                self.edges.append(Edge(node1, neighbor, rule.node1_connection[color]))
                            if color in rule.node2_connection:
                                self.edges.append(Edge(node2, neighbor, rule.node2_connection[color]))
                    case DeleteRule():
                        # Rewiring
                        for n1, color1 in neighbors:
                            for n2, color2 in neighbors:
                                if n1.id != n2.id and (color1, color2) in rule.rewiring:
                                    # This if is to prevent two edges appearning for rules that connect the same colors
                                    if color1 == color2 and n1.id < n2.id:
                                        continue
                                    self.edges.append(Edge(n1, n2, rule.rewiring[(color1, color2)]))

                return True
        return False

    def draw(self, mark_red: Node | None = None):
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node.id)
        for edge in self.edges:
            G.add_edge(edge.v1.id, edge.v2.id, color=edge.color)
        edge_colors = [G[u][v]["color"] for u, v in G.edges()]
        node_colors = [
            "lightcoral" if mark_red is not None and node == mark_red.id else "skyblue" for node in G.nodes()
        ]
        nx.draw(G, labels={node.id: node.label for node in self.nodes}, node_color=node_colors, edge_color=edge_colors)
        plt.show()

    def seems_isomorphic_to(self, other: Self) -> bool:
        colors1 = sorted(
            [
                sorted(edge.color for edge in self.edges if edge.v1.id == node or edge.v2.id == node)
                for node in self.nodes
            ]
        )
        colors2 = sorted(
            [
                sorted(edge.color for edge in other.edges if edge.v1.id == node or edge.v2.id == node)
                for node in other.nodes
            ]
        )

        return colors1 == colors2
