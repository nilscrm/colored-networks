from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from colored_networks.network import ColoredNetwork, Edge, Rule, Node

"""
Meaning of the colors
black: body of a lambda abstraction
red: function of an application
blue: argument of an application
green: Chain of duplication nodes from lambda abstraction
yellow: Variable duplicator node binds
purple: lambda in beta redex got remove, now application node should be removed
pink: input for duplication node (=> copy to yellow variable)
lime: variable should be replaced by the graph on the other end
maroon: delete graph (happens when argument is placed into a lambda that never uses this argument)
"""
beta_reduction_rules = [
    # beta reduction (lambda)
    Rule(name="beta reduction (lambda)", input={'red':1, 'black':1, 'green':1}, new_edges=[], internal_rewiring={}, external_rewiring={('red', 'green'): 'purple', ('black', 'red'): 'black'}),
    # beta reduction (application)
    Rule(name="beta reduction (app)", input={'purple':1, 'blue':1, 'black':1}, new_edges=[], internal_rewiring={}, external_rewiring={('purple', 'blue'): 'pink'}),
    Rule(name="beta reduction (app) as left child", input={'purple':1, 'blue':1, 'black':1, 'red':1}, new_edges=[], internal_rewiring={}, external_rewiring={('purple', 'blue'): 'pink', ('black', 'red'): 'red'}),
    # duplicator (application)
    Rule(name="duplicate", input={'pink':1, 'yellow':1}, new_edges=[], internal_rewiring={}, external_rewiring={('pink', 'yellow'): 'lime'}),
    # var substitution
    Rule(name="var substitution (root)", input={'lime':1}, new_edges=[], internal_rewiring={}, external_rewiring={}),
    Rule(name="var substitution as lambda body", input={'lime':1, 'black': 1}, new_edges=[], internal_rewiring={}, external_rewiring={('black', 'lime'): 'black'}),
    # Deletion
    Rule(name="detect deletion", input={'pink': 1}, new_edges=[], internal_rewiring={'pink': [(Node(0, "Δ"), "maroon")]}, external_rewiring={}),
    Rule(name="delete lambda", input={'maroon': 1, 'black': 1, 'green': 1}, new_edges=[], internal_rewiring={}, external_rewiring={('black', 'maroon'): 'maroon'}),
    Rule(name="delete application", input={'maroon': 1, 'red': 1, 'blue': 1}, new_edges=[], internal_rewiring={}, external_rewiring={('red', 'maroon'): 'maroon', ('blue', 'maroon'): 'maroon'}),
    # TODO: Mark the extra dup node also for deletion
    Rule(name="delete variable", input={'maroon': 1, 'yellow': 1}, new_edges=[], internal_rewiring={}, external_rewiring={}),
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
    def to_colored_network_edges(self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]) -> tuple[Node, list[Edge], int]:
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
    
    def to_colored_network_edges(self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]) -> tuple[Node, list[Edge], int]:
        abs_node = Node(next_vertex_id, label=f"λ{self.var}")
        dup_node = Node(next_vertex_id + 1, label="Δ")
        var_dup_nodes[self.var] = (dup_node, False)
        body_node, body_edges, next_vertex_id = self.body.to_colored_network_edges(next_vertex_id + 2, var_dup_nodes)
        edges = [Edge(abs_node, body_node, 'black'), Edge(abs_node, dup_node, 'green')] + body_edges
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
    
    def to_colored_network_edges(self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]) -> tuple[Node, list[Edge], int]:
        func_root, func_edges, next_vertex_id = self.func.to_colored_network_edges(next_vertex_id, var_dup_nodes)
        arg_root, arg_edges, next_vertex_id = self.arg.to_colored_network_edges(next_vertex_id, var_dup_nodes)
        app_node = Node(next_vertex_id, label='⋅')
        edges = [Edge(app_node, func_root, 'red'), Edge(app_node, arg_root, 'blue')] + func_edges + arg_edges
        return app_node, edges, next_vertex_id + 1
    
    def clone(self) -> Self:
        return App(self.func.clone(), self.arg.clone())


@dataclass
class Var(LambdaTerm):
    name: str

    def substitute(self, var, replacement):
        return replacement if self.name == var else self
    
    def to_colored_network_edges(self, next_vertex_id, var_dup_nodes: dict[str, (Node, bool)]) -> tuple[Node, list[Edge], int]:
        var_node = Node(next_vertex_id, label=self.name)
        dup_node, used = var_dup_nodes[self.name]
        if used:
            new_dup_node = Node(next_vertex_id + 1, label="Δ")
            edges = [Edge(dup_node, new_dup_node, 'green'), Edge(new_dup_node, var_node, 'yellow')]
            var_dup_nodes[self.name] = (dup_node, True)
            return var_node, edges, next_vertex_id + 2
        else:
            edges = [Edge(dup_node, var_node, 'yellow')]
            var_dup_nodes[self.name] = (dup_node, True)
            return var_node, edges, next_vertex_id + 1

    def clone(self) -> Self:
        return Var(self.name)

