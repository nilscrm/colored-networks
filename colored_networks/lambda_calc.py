from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from colored_networks.network import ColoredNetwork, Edge, Rule, Node


beta_reduction_rules = [
    # beta reduction (abstraction)
    Rule(input={'red':1, 'black':1, 'green':1}, new_edges=[], internal_rewiring={}, external_rewiring={('red', 'green'): 'purple', ('black', 'red'): 'black'}),
    # beta reduction (application)
    Rule(input={'purple':1, 'blue':1, 'black':1}, new_edges=[], internal_rewiring={}, external_rewiring={('purple', 'blue'): 'pink'}),
    # duplicator (application)
    Rule(input={'pink':1, 'yellow':1}, new_edges=[], internal_rewiring={}, external_rewiring={('pink', 'yellow'): 'lime'}),
    # var substitution (root)
    Rule(input={'lime':1}, new_edges=[], internal_rewiring={}, external_rewiring={}),
]


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
    def substitute(self, var, replacement):
        ...

    @abstractmethod
    def to_colored_network_edges(self, next_vertex_id, var_nodes: dict[str, Node]) -> tuple[Node, list[Edge], int]:
        ...

    def to_colored_network(self) -> ColoredNetwork:
        return ColoredNetwork(rules=beta_reduction_rules, edges=self.to_colored_network_edges(0, {})[1])
    
    @abstractmethod
    def clone(self) -> Self:
        ...



@dataclass
class Abs(LambdaTerm):
    var: str
    body: LambdaTerm

    def substitute(self, var, replacement):
        if self.var == var:
            return self
        self.body = self.body.substitute(var, replacement)
        return self
    
    def to_colored_network_edges(self, next_vertex_id, var_nodes: dict[str, Node]) -> tuple[Node, list[Edge], int]:
        abs_node = next_vertex_id
        var_nodes[self.var] = abs_node
        body_node, body_edges, next_vertex_id = self.body.to_colored_network_edges(next_vertex_id + 1, var_nodes)
        edges = [Edge(abs_node, body_node, 'black')] + body_edges
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
    
    def to_colored_network_edges(self, next_vertex_id, var_nodes: dict[str, Node]) -> tuple[Node, list[Edge], int]:
        func_root, func_edges, next_vertex_id = self.func.to_colored_network_edges(next_vertex_id, var_nodes)
        arg_root, arg_edges, next_vertex_id = self.arg.to_colored_network_edges(next_vertex_id, var_nodes)
        app_node = next_vertex_id
        edges = [Edge(app_node, func_root, 'red'), Edge(next_vertex_id, arg_root, 'blue')] + func_edges + arg_edges
        return app_node, edges, next_vertex_id + 1
    
    def clone(self) -> Self:
        return App(self.func.clone(), self.arg.clone())


@dataclass
class Var(LambdaTerm):
    name: str

    def substitute(self, var, replacement):
        return replacement if self.name == var else self
    
    def to_colored_network_edges(self, next_vertex_id, var_nodes: dict[str, Node]) -> tuple[Node, list[Edge], int]:
        var_node = next_vertex_id
        dup_node = next_vertex_id + 1
        edges = [Edge(dup_node, var_nodes[self.name], 'green'), Edge(dup_node, var_node, 'yellow')]
        var_nodes[self.name] = dup_node
        return var_node, edges, next_vertex_id + 2

    def clone(self) -> Self:
        return Var(self.name)

