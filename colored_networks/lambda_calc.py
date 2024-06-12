from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from colored_networks.beta_reduction_rules import beta_reduction_rules
from colored_networks.colored_network import ColoredNetwork, Edge, Node


class LambdaTerm(ABC):
    def reduce(self):
        match self:
            case App(Abs(var, body), arg):
                return body.substitute(var, arg).reduce()
            case App(func, arg):
                return App(func.reduce(), arg.reduce())
            case Abs(var, body):
                return Abs(var, body.reduce())
            case Var():
                return self

    @abstractmethod
    def substitute(self, var, replacement): ...

    @abstractmethod
    def to_colored_network_edges(
        self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]
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

    def substitute(self, var, replacement):
        if self.var == var:
            return self
        self.body = self.body.substitute(var, replacement)
        return self

    def to_colored_network_edges(
        self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]
    ) -> tuple[Node, list[Edge], int]:
        abs_node = Node(next_vertex_id, label=f"λ{self.var}")
        # We always attach at least 1 duplicater node to the lambda abstraction to indicate to the node that it is a
        # lambda abstraction
        dup_node = Node(next_vertex_id + 1, label="Δ")
        var_dup_nodes[self.var] = (dup_node, False)
        body_node, body_edges, next_vertex_id = self.body.to_colored_network_edges(next_vertex_id + 2, var_dup_nodes)
        edges = [Edge(abs_node, body_node, "black"), Edge(abs_node, dup_node, "green")] + body_edges
        return abs_node, edges, next_vertex_id

    def clone(self) -> Self:
        return Abs(self.var, self.body.clone())


@dataclass
class App(LambdaTerm):
    func: LambdaTerm
    arg: LambdaTerm

    def substitute(self, var, replacement):
        self.func = self.func.substitute(var, replacement)
        self.arg = self.arg.substitute(var, replacement)
        return self

    def to_colored_network_edges(
        self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]
    ) -> tuple[Node, list[Edge], int]:
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

    def substitute(self, var, replacement):
        return replacement if self.name == var else self

    def to_colored_network_edges(
        self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]
    ) -> tuple[Node, list[Edge], int]:
        var_node = Node(next_vertex_id, label=self.name)
        dup_node, used = var_dup_nodes[self.name]
        if used:
            new_dup_node = Node(next_vertex_id + 1, label="Δ")
            edges = [Edge(dup_node, new_dup_node, "green"), Edge(new_dup_node, var_node, "yellow")]
            var_dup_nodes[self.name] = (dup_node, True)
            return var_node, edges, next_vertex_id + 2
        else:
            edges = [Edge(dup_node, var_node, "yellow")]
            var_dup_nodes[self.name] = (dup_node, True)
            return var_node, edges, next_vertex_id + 1

    def clone(self) -> Self:
        return Var(self.name)
