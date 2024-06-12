from colored_networks.network import Rule, Node

"""
Meaning of the colors

black/dimgray: body of a lambda abstraction
red: function of an application
orangered: left child of application after lambda node was removed from it

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
beta_reduction_rules = [
    # beta reduction (lambda)
    Rule(
        name="beta reduction (lambda)",
        input={"red": 1, "black": 1, "green": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("red", "green"): "purple", ("black", "red"): "orangered"},
    ),
    # beta reduction (application)
    Rule(
        name="beta reduction (app) step 1",
        input={"purple": 1, "blue": 1, "orangered": 1},
        new_edges=[],
        internal_rewiring={
            "purple": [(Node(0, "⋅"), "purple")],
            "orangered": [(Node(0, "⋅"), "orangered")],
            "blue": [(Node(0, "⋅"), "cornflowerblue")],
        },
        external_rewiring={},
    ),
    Rule(
        name="beta reduction (connecter)",
        input={"navy": 1, "cornflowerblue": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("navy", "cornflowerblue"): "slateblue"},
    ),
    Rule(
        name="beta reduction (app) step 2",
        input={"purple": 1, "slateblue": 1, "orangered": 1},
        new_edges=[],
        internal_rewiring={"purple": [(Node(0), "fuchsia")]},
        external_rewiring={("purple", "slateblue"): "pink"},
    ),
    Rule(
        name="beta reduction (app) as left child step 1",
        input={"purple": 1, "blue": 1, "orangered": 1, "red": 1},
        new_edges=[],
        internal_rewiring={
            "purple": [(Node(0, "⋅"), "purple")],
            "orangered": [(Node(0, "⋅"), "orangered")],
            "blue": [(Node(0, "⋅"), "cornflowerblue")],
            "red": [(Node(0, "⋅"), "red")],
        },
        external_rewiring={},
    ),
    Rule(
        name="beta reduction (app) as left child step 2",
        input={"purple": 1, "slateblue": 1, "orangered": 1, "red": 1},
        new_edges=[],
        internal_rewiring={"purple": [(Node(0), "fuchsia")]},
        external_rewiring={("purple", "slateblue"): "pink", ("orangered", "red"): "red"},
    ),
    Rule(
        name="beta reduction (app) as right child step 1",
        input={"purple": 1, "blue": 1, "orangered": 1, "navy": 1},
        new_edges=[],
        internal_rewiring={
            "purple": [(Node(0, "⋅"), "purple")],
            "orangered": [(Node(0, "⋅"), "orangered")],
            "blue": [(Node(0, "⋅"), "cornflowerblue")],
            "navy": [(Node(0, "⋅"), "navy")],
        },
        external_rewiring={},
    ),
    Rule(
        name="beta reduction (app) as right child step 2",
        input={"purple": 1, "slateblue": 1, "orangered": 1, "navy": 1},
        new_edges=[],
        internal_rewiring={"purple": [(Node(0), "fuchsia")]},
        external_rewiring={("purple", "slateblue"): "pink", ("orangered", "navy"): "navy"},
    ),
    Rule(
        name="beta reduction (app) as lambda child step 1",
        input={"purple": 1, "blue": 1, "orangered": 1, "black": 1},
        new_edges=[],
        internal_rewiring={
            "purple": [(Node(0, "⋅"), "purple")],
            "orangered": [(Node(0, "⋅"), "orangered")],
            "blue": [(Node(0, "⋅"), "cornflowerblue")],
            "black": [(Node(0, "⋅"), "black")],
        },
        external_rewiring={},
    ),
    Rule(
        name="beta reduction (app) as lambda child step 2",
        input={"purple": 1, "slateblue": 1, "orangered": 1, "black": 1},
        new_edges=[],
        internal_rewiring={"purple": [(Node(0), "fuchsia")]},
        external_rewiring={("purple", "slateblue"): "pink", ("orangered", "black"): "black"},
    ),
    # Node duplication
    Rule(
        name="var substitution (dup)",
        input={"pink": 1, "fuchsia": 1, "yellow": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("pink", "yellow"): "lime"},
    ),
    Rule(
        name="detect duplication",
        input={"pink": 1, "yellow": 1, "green": 1, "fuchsia": 1},
        new_edges=[],
        internal_rewiring={
            "pink": [(Node(0, "Δ"), "orange")],
            "yellow": [(Node(0, "Δ"), "yellow")],
            "green": [(Node(0, "Δ"), "green")],
        },
        external_rewiring={},
    ),
    Rule(
        name="lambda duplication",
        input={"black": 1, "green": 1, "orange": 1},
        new_edges=[],
        internal_rewiring={
            "black": [(Node(0, "λ"), "black"), (Node(1, "λ"), "dimgray")],
            "green": [(Node(0, "λ"), "gold"), (Node(1, "λ"), "goldenrod")],
            "orange": [(Node(0, "λ"), "pink"), (Node(1, "λ"), "magenta")],
        },
        external_rewiring={},
    ),
    Rule(
        name="var duplication (as lambda body)",
        input={"black": 1, "dimgray": 1, "yellow": 1},
        new_edges=[],
        internal_rewiring={
            "black": [(Node(0, "_"), "black")],
            "dimgray": [(Node(1, "_"), "black")],
            "yellow": [(Node(0, "_"), "yellow"), (Node(1, "_"), "olive")],
        },
        external_rewiring={},
    ),
    Rule(
        name="dup node duplication",
        input={"gold": 1, "goldenrod": 1, "yellow": 1, "olive": 1},
        new_edges=[],
        internal_rewiring={
            "gold": [(Node(0, "Δ"), "green")],
            "goldenrod": [(Node(1, "Δ"), "green")],
            "yellow": [(Node(0, "Δ"), "yellow")],
            "olive": [(Node(1, "Δ"), "yellow")],
        },
        external_rewiring={},
    ),
    Rule(
        name="Propagation of duplicated nodes at dup node",
        input={"green": 1, "yellow": 1, "pink": 1, "magenta": 1},
        new_edges=[],
        internal_rewiring={
            "green": [(Node(0), "fuchsia")],
        },
        external_rewiring={
            ("pink", "yellow"): "lime",
            ("green", "magenta"): "pink",
        },
    ),
    # var substitution
    Rule(name="var substitution (root)", input={"lime": 1}, new_edges=[], internal_rewiring={}, external_rewiring={}),
    Rule(
        name="var substitution as lambda body",
        input={"lime": 1, "black": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("black", "lime"): "black"},
    ),
    Rule(
        name="var substitution as application function",
        input={"lime": 1, "red": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("red", "lime"): "red"},
    ),
    Rule(
        name="var substitution as application argument",
        input={"lime": 1, "navy": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("navy", "lime"): "navy"},
    ),
    # Deletion
    Rule(
        name="detect deletion",
        input={"pink": 1, "fuchsia": 1},
        new_edges=[],
        internal_rewiring={"pink": [(Node(0, "Δ"), "maroon")]},
        external_rewiring={},
    ),
    Rule(
        name="delete lambda",
        input={"maroon": 1, "black": 1, "green": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("black", "maroon"): "maroon"},
    ),
    Rule(
        name="delete connecter",
        input={"maroon": 1, "navy": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("navy", "maroon"): "maroon"},
    ),
    Rule(
        name="delete application",
        input={"maroon": 1, "red": 1, "blue": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("red", "maroon"): "maroon", ("blue", "maroon"): "maroon"},
    ),
    # TODO: Delte navy node
    Rule(
        name="delete variable",
        input={"maroon": 1, "yellow": 1},
        new_edges=[],
        internal_rewiring={
            "yellow": [(Node(0, "_"), "darkred")],
        },
        external_rewiring={},
    ),
    Rule(
        name="delete dup node",
        input={"darkred": 1},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={},
    ),
    Rule(
        name="delete dup node (sandwiched)",
        input={"darkred": 1, "green": 2},
        new_edges=[],
        internal_rewiring={},
        external_rewiring={("green", "green"): "green"},
    ),
]
