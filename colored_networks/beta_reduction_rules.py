from colored_networks.colored_network import SplitRule, DeleteRule

"""
Meaning of the colors

black/dimgray: body of a lambda abstraction
red: function of an application
orangered: left child of application after lambda node was removed from it
tomato: connect app node and dup node that has just been maked with fuchsia.
    Next the app node should remove itself to let the dup node copy the argument.

blue: argument of an application
navy: parent node (this node is argument of an application)
cornflowerblue: prepare right child for substitution
slateblue: right child about to be substituted

green: Chain of duplication nodes from lambda abstraction
yellow/olive: Variable duplicator node binds
purple: lambda in beta redex got removed, now application node should be removed
pink: input for duplication node (=> copy to yellow variable)
fuchsia: indicator that duplicator should duplicate
magenta: duplicated node
orange: Node duplication
gold/goldenrod: duplication of dup node
lime: variable should be replaced by the graph on the other end
maroon: delete graph (happens when argument is placed into a lambda that never uses this argument)
"""
beta_reduction_rules = (
    [
        # beta reduction (lambda)
        DeleteRule(
            name="beta reduction (lambda)",
            input={"red": 1, "black": 1, "green": 1},
            rewiring={("red", "green"): "purple", ("black", "red"): "orangered"},
        )
    ]
    + [
        SplitRule(
            name="beta reduction (app) step 1",
            input={"purple": 1, "blue": 1, "orangered": 1} | {p: 1 for p in parent},
            node1_connection={"purple": "purple", "orangered": "orangered", "blue": "cornflowerblue"}
            | {p: p for p in parent},
            node2_connection={},
            rewiring={},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        DeleteRule(
            name="beta reduction (connecter)",
            input={"navy": 1, "cornflowerblue": 1},
            rewiring={("navy", "cornflowerblue"): "slateblue"},
        ),
    ]
    + [
        SplitRule(
            name="beta reduction (app) step 2",
            input={"purple": 1, "slateblue": 1, "orangered": 1} | {p: 1 for p in parent},
            node1_connection={"purple": "fuchsia"},
            node2_connection={"purple": "purple", "orangered": "tomato", "slateblue": "slateblue"}
            | {p: p for p in parent},
            rewiring={},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        DeleteRule(
            name="beta reduction (app) step 3",
            input={"purple": 1, "slateblue": 1, "tomato": 1} | {p: 1 for p in parent},
            rewiring={("purple", "slateblue"): "pink"} | {("tomato", p): p for p in parent},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        # Node duplication
        DeleteRule(
            name="var substitution (dup)",
            input={"pink": 1, "fuchsia": 1, "yellow": 1},
            rewiring={("pink", "yellow"): "lime"},
        ),
        SplitRule(
            name="detect duplication",
            input={"pink": 1, "yellow": 1, "green": 1, "fuchsia": 1},
            node1_connection={"pink": "orange", "yellow": "yellow", "green": "green"},
            node2_connection={},
            rewiring={},
        ),
        SplitRule(
            name="lambda duplication",
            input={"black": 1, "green": 1, "orange": 1},
            node1_connection={"black": "black", "green": "gold", "orange": "pink"},
            node2_connection={"black": "dimgray", "green": "goldenrod", "orange": "magenta"},
            rewiring={},
        ),
        SplitRule(
            name="var duplication (as lambda body)",
            input={"black": 1, "dimgray": 1, "yellow": 1},
            node1_connection={"black": "black", "yellow": "yellow"},
            node2_connection={"dimgray": "black", "yellow": "olive"},
            rewiring={},
        ),
        SplitRule(
            name="dup node duplication",
            input={"gold": 1, "goldenrod": 1, "yellow": 1, "olive": 1},
            node1_connection={"gold": "green", "yellow": "yellow"},
            node2_connection={"goldenrod": "green", "olive": "yellow"},
            rewiring={},
        ),
        SplitRule(
            name="Propagation of duplicated nodes at dup node",
            input={"green": 1, "yellow": 1, "pink": 1, "magenta": 1},
            node1_connection={"green": "fuchsia"},
            node2_connection={},
            rewiring={
                ("pink", "yellow"): "lime",
                ("green", "magenta"): "pink",
            },
        ),
    ]
    + [
        DeleteRule(
            name="var substitution",
            input={"lime": 1} | {p: 1 for p in parent},
            rewiring={(p, "lime"): p for p in parent},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        # Deletion
        SplitRule(
            name="detect deletion",
            input={"pink": 1, "fuchsia": 1},
            node1_connection={"pink": "maroon"},
            node2_connection={},
            rewiring={},
        ),
        DeleteRule(
            name="delete lambda",
            input={"maroon": 1, "black": 1, "green": 1},
            rewiring={("black", "maroon"): "maroon"},
        ),
        DeleteRule(
            name="delete connecter",
            input={"maroon": 1, "navy": 1},
            rewiring={("navy", "maroon"): "maroon"},
        ),
        DeleteRule(
            name="delete application",
            input={"maroon": 1, "red": 1, "blue": 1},
            rewiring={("red", "maroon"): "maroon", ("blue", "maroon"): "maroon"},
        ),
        # TODO: Delte navy node
        SplitRule(
            name="delete variable",
            input={"maroon": 1, "yellow": 1},
            node1_connection={"yellow": "darkred"},
            node2_connection={},
            rewiring={},
        ),
        DeleteRule(
            name="delete dup node",
            input={"darkred": 1},
            rewiring={},
        ),
        DeleteRule(
            name="delete dup node (sandwiched)",
            input={"darkred": 1, "green": 2},
            rewiring={("green", "green"): "green"},
        ),
        DeleteRule(
            name="Delete singleton node",
            input={},
            rewiring={},
        ),
    ]
)
