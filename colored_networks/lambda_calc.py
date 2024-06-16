from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from colored_networks.beta_reduction_rules import beta_reduction_rules
from colored_networks.colored_network import ColoredNetwork, Edge, Node


class LambdaTerm(ABC):
    @abstractmethod
    def to_colored_network_edges(
        self, next_vertex_id, var_dup_nodes: dict[str, Node]
    ) -> tuple[Node, list[Edge], int]: ...

    def to_colored_network(self) -> ColoredNetwork:
        edges = self.to_colored_network_edges(0, {})[1]
        nodes = list({edge.v1 for edge in edges} | {edge.v2 for edge in edges})
        return ColoredNetwork(nodes, edges, beta_reduction_rules)

    @abstractmethod
    def clone(self) -> Self: ...


@dataclass
class Abs(LambdaTerm):
    var: str
    body: LambdaTerm

    def to_colored_network_edges(self, next_vertex_id, var_dup_nodes: dict[str, Node]) -> tuple[Node, list[Edge], int]:
        abs_node = Node(next_vertex_id, label=f"λ{self.var}")
        var_dup_nodes[self.var] = abs_node
        body_node, body_edges, next_vertex_id = self.body.to_colored_network_edges(next_vertex_id + 1, var_dup_nodes)
        edges = [Edge(abs_node, body_node, "black")] + body_edges
        return abs_node, edges, next_vertex_id

    def clone(self) -> Self:
        return Abs(self.var, self.body.clone())


@dataclass
class App(LambdaTerm):
    func: LambdaTerm
    arg: LambdaTerm

    def to_colored_network_edges(self, next_vertex_id, var_dup_nodes: dict[str, Node]) -> tuple[Node, list[Edge], int]:
        func_root, func_edges, next_vertex_id = self.func.to_colored_network_edges(next_vertex_id, var_dup_nodes)
        arg_root, arg_edges, next_vertex_id = self.arg.to_colored_network_edges(next_vertex_id, var_dup_nodes)
        app_node = Node(next_vertex_id, label="⋅")
        connecter_node = Node(next_vertex_id + 1)
        edges = (
            [
                Edge(app_node, func_root, "red"),
                Edge(app_node, connecter_node, "blue"),
                Edge(connecter_node, arg_root, "navy"),
            ]
            + func_edges
            + arg_edges
        )
        return app_node, edges, next_vertex_id + 2

    def clone(self) -> Self:
        return App(self.func.clone(), self.arg.clone())


@dataclass
class Var(LambdaTerm):
    name: str

    def to_colored_network_edges(self, next_vertex_id, var_dup_nodes: dict[str, Node]) -> tuple[Node, list[Edge], int]:
        var_node = Node(next_vertex_id, label=self.name)
        parent_dup_node = var_dup_nodes[self.name]
        dup_connecter_node = Node(next_vertex_id + 1)
        new_dup_node = Node(next_vertex_id + 2, label="Δ")
        edges = [
            Edge(parent_dup_node, dup_connecter_node, "green"),
            Edge(dup_connecter_node, new_dup_node, "forestgreen"),
            Edge(new_dup_node, var_node, "yellow"),
        ]
        var_dup_nodes[self.name] = new_dup_node
        return var_node, edges, next_vertex_id + 3

    def clone(self) -> Self:
        return Var(self.name)
