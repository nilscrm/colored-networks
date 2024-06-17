from colored_networks.colored_network import SplitRule, DeleteRule

NODE_PARENTS = [
    [],
    ["black"],
    ["red"],
    ["navy"],
    ["maroon"],
    ["slateblue"],
    ["orange", "magenta"],
    ["lightgray", "darkgray"],
    ["lightsalmon", "salmon"],
    ["mediumblue", "midnightblue"],
]

"""
Meaning of the colors

black: body of a lambda abstraction
lightgray/darkgray: connects duplicated lambda terms to their not yet duplicated child
red: function of an application
lightsalmon/salmon: connects duplicated app nodes to their not yet duplicated left child
coral: connects application node to lambda function after lambda function has produced indicator node for app node
orangered: left child of application after lambda node was removed from it
tomato: connect app node and dup node that has just been maked with fuchsia.
    Next the app node should remove itself to let the dup node copy the argument.

blue: argument of an application
lightblue/darkblue: connects duplicated app nodes to their not yet duplicated right child
navy: parent node (this node is argument of an application)
mediumblue/midnightblue: connects duplicated connecter nodes to their not yet duplicated child
cornflowerblue: prepare right child for substitution
slateblue: right child about to be substituted
aqua: connects a app node being beta reduced to its parant app. This way we prevent the parent node from being reduced.

green/forestgreen: Chain of dup nodes from lambda abstraction, they always have a connector node between then,
    the parent connected with forestgreen and the child connected with green
seagreen/mediumseagreen: Chain on dup nodes that should be duplicated
springgreen/mediumspringgreen: Connectes duplicated dup nodes to their not yet duplicated parent dup node
lighgreen/darkgreen: Connect duplicated lambda nodes to their not yet duplicated dup node

yellow: Variable duplicator node binds
goldenrod/darkgoldenrod: Connectes duplicated dup nodes from duplicated chain to not yet duplicated variable node
khaki/darkkhaki: Connect duplicated variable to their not yet duplicated dup node
gold: When duplicating a dup node this edge gets created for one of the variable nodes to connect up the cloned dup
    nodes

purple: lambda in beta redex got removed, now application node should be removed
pink: input for duplication node (=> copy to yellow variable)
fuchsia: indicator that duplicator should duplicate
magenta: duplicated node
orange: Node duplication
lime: variable should be replaced by the graph on the other end
maroon: delete graph (happens when argument is placed into a lambda that never uses this argument)
"""
beta_reduction_rules = (
    [
        # -- Beta Reduction
        # Detects a lambda abstraction beneath an application node (red) and marks it ready for beta reduction with
        # coral and creates a marker node connected to the app node with tan. This node will stay there until the
        # appliation node has finished beta reducing.
        SplitRule(
            name="beta reduction (lambda), bound variable not used, step 1",
            input={"black": 1, "red": 1},
            node1_connection={"black": "black", "red": "coral"},
            node2_connection={"red": "tan"},
        ),
        # Removes the lambda node, marking the app node ready for beta reduction with orangered.
        DeleteRule(
            name="beta reduction (lambda), bound variable not used, step 2",
            input={"black": 1, "coral": 1},
            rewiring={("black", "coral"): "orangered"},
        ),
        # Same as above but now the lambda term has a variable bound to it (green connected to dup node).
        SplitRule(
            name="beta reduction (lambda), step 1",
            input={"black": 1, "red": 1, "green": 1},
            node1_connection={"black": "black", "red": "coral", "green": "green"},
            node2_connection={"red": "tan"},
        ),
        # Same as with no bound variable. The difference is that the dup node is connected to the app node with purple.
        # The app node is then supposed to pass the argument to the function to the dup node to substitute the bound
        # variables.
        DeleteRule(
            name="beta reduction (lambda), step 2",
            input={"coral": 1, "black": 1, "green": 1},
            rewiring={("coral", "green"): "purple", ("black", "coral"): "orangered"},
        ),
        # Argument is connected with an additional connector node (blue). We will mark it for contraction with
        # cornflowerblue.
        # In case the parent is an app node we need to prevent the parent node from beta reducing.
        # Otherwise this app node will end up with two slateblue connection which it can't tell apart.
        # To prevent this we turn the parent connection into aqua.
        SplitRule(
            name="beta reduction (app) step 1 (aqua)",
            input={"tan": 1, "purple": 1, "blue": 1, "orangered": 1, "navy": 1},
            node1_connection={
                "tan": "tan",
                "purple": "purple",
                "orangered": "orangered",
                "blue": "cornflowerblue",
                "navy": "aqua",
            },
            node2_connection={},
        ),
    ]
    + [
        # Argument is connected with an additional connector node (blue). We will mark it for contraction with
        # cornflowerblue.
        SplitRule(
            name="beta reduction (app) step 1",
            input={"tan": 1, "purple": 1, "blue": 1, "orangered": 1} | {p: 1 for p in parent},
            node1_connection={"tan": "tan", "purple": "purple", "orangered": "orangered", "blue": "cornflowerblue"}
            | {p: p for p in parent},
            node2_connection={},
        )
        for parent in [
            [],
            ["black"],
            ["red"],
            ["maroon"],
            ["orange", "magenta"],
            ["lightgray", "darkgray"],
            ["lightsalmon", "salmon"],
            ["mediumblue", "midnightblue"],
        ]
    ]
    + [
        # Contract the argument connector node to make the argument available for substitution.
        DeleteRule(
            name="beta reduction (arg connecter)",
            input={"navy": 1, "cornflowerblue": 1},
            rewiring={("navy", "cornflowerblue"): "slateblue"},
        ),
    ]
    + [
        # Before passing along the argument, we mark the dup node ready for substitution with fuchsia.
        SplitRule(
            name="beta reduction (app) step 2",
            input={"tan": 1, "purple": 1, "slateblue": 1, "orangered": 1} | {p: 1 for p in parent},
            node1_connection={"purple": "fuchsia"},
            node2_connection={"tan": "tan", "purple": "purple", "orangered": "tomato", "slateblue": "slateblue"}
            | {p: p for p in parent},
        )
        for parent in [
            [],
            ["black"],
            ["red"],
            ["aqua"],
            ["maroon"],
            ["slateblue"],
            ["orange", "magenta"],
            ["lightgray", "darkgray"],
            ["lightsalmon", "salmon"],
            ["mediumblue", "midnightblue"],
        ]
    ]
    + [
        # Remove app node, connect argument (slateblue) to the dup node (purple) for substitution and connect function
        # body (tomato) to parent node.
        DeleteRule(
            name="beta reduction (app) step 3",
            input={"tan": 1, "purple": 1, "slateblue": 1, "tomato": 1} | {p: 1 for p in parent},
            rewiring={("purple", "slateblue"): "pink"} | {("tomato", p): p for p in parent},
        )
        for parent in NODE_PARENTS
    ]
    + [
        # Same as above but in the case we blocked the parant app node from reducting with aqua, we need to turn it
        # back to navy.
        DeleteRule(
            name="beta reduction (app) step 3",
            input={"tan": 1, "purple": 1, "slateblue": 1, "tomato": 1, "aqua": 1},
            rewiring={("purple", "slateblue"): "pink", ("tomato", "aqua"): "navy"},
        )
    ]
    + [
        # -- Variable substitution --
        # Pass the arugment to be substituted (pink) to the acutal var node (forestgreen) and mark it ready for
        # substitution with fuchsia. Fuchsia is added so that the other end of the lime edge doesn't think it's the
        # variable that needs replacement.
        DeleteRule(
            name="dup node connecter, substitution propagation",
            input={"pink": 1, "fuchsia": 1, "forestgreen": 1},
            rewiring={("forestgreen", "fuchsia"): "fuchsia", ("pink", "forestgreen"): "pink"},
        ),
    ]
    + [
        # When there is no further var node connected (no green) we can just substitute the argument (pink) into the
        # variable.
        DeleteRule(
            name="var substitution (dup)",
            input={"pink": 1, "fuchsia": 1} | {p: 1 for p in parent},
            rewiring={("pink", p): p for p in parent},
        )
        for parent in NODE_PARENTS
    ]
    + [
        # If there is another var node (green) then we need to clone the argument to pass along to the next one.
        # This is by connecting both this variable and the next var connector node (green) to the argument with orange
        # and magenta. Then the argument gets cloned (see below for cloning rules).
        SplitRule(
            name="detect argument duplication",
            input={"pink": 1, "fuchsia": 1, "green": 1} | {p: 1 for p in parent},
            node1_connection={"pink": "orange", "fuchsia": "fuchsia"} | {p: p for p in parent},
            # Since we can't connect other nodes with a SplitRule be will create an additional var connector node.
            # After the argument has been cloned this node will just pass the argument along.
            node2_connection={"pink": "magenta", "green": "forestgreen", "fuchsia": "fuchsia"},
        )
        for parent in NODE_PARENTS
    ]
    # -- Duplication --
    + [
        SplitRule(
            name="lambda duplication, bound variable not used",
            input={"black": 1} | {p: 1 for p in parents},
            node1_connection={"black": "lightgray"} | {parents[0]: regular_color},
            node2_connection={"black": "darkgray"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["orange", "magenta"], "pink"),
            (["lightgray", "darkgray"], "black"),
            (["lightsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        # When duplicating a lambda term, first duplicate the entire chain of var connector nodes.
        # The reason for this is that when a variable is cloned we need to know whether the lambda that binds this
        # variable was also cloned or not. By first cloning the var connector node chain we know this.
        SplitRule(
            name="lambda duplication, step 1",
            input={"black": 1, "green": 1} | {p: 1 for p in parents},
            node1_connection={"black": "black", "green": "seagreen"} | {p: p for p in parents},
            node2_connection={},
        )
        for parents in [
            ("orange", "magenta"),
            ("lightgray", "darkgray"),
            ("lightsalmon", "salmon"),
            ("mediumblue", "midnightblue"),
        ]
    ]
    + [
        # Go down var node chain and mark nodes for duplciation
        SplitRule(
            name="var connector node chain duplication, step 1",
            input={"seagreen": 1, "forestgreen": 1},
            node1_connection={"seagreen": "seagreen", "forestgreen": "mediumseagreen"},
            node2_connection={},
        )
    ]
    + [
        SplitRule(
            name="var node chain duplication, step 1",
            input={"mediumseagreen": 1, "green": 1} | {p: 1 for p in parents},
            node1_connection={"mediumseagreen": "mediumseagreen", "green": "seagreen"} | {p: p for p in parents},
            node2_connection={},
        )
        for parents in NODE_PARENTS
    ]
    + [
        # Once last var node has been reached, start with duplicating the var connector nodes.
        SplitRule(
            name="var node chain duplication (one neighbors), step 2",
            input={"mediumseagreen": 1} | {p: 1 for p in parents},
            node1_connection={"mediumseagreen": "springgreen"} | {p: p for p in parents},
            node2_connection={},
        )
        for parents in NODE_PARENTS
    ]
    + [
        # Go up the dup node chain and duplicate the nodes
        SplitRule(
            name="var connector node chain duplication, step 2",
            input={"seagreen": 1, "springgreen": 1},
            node1_connection={"seagreen": "lightgreen", "springgreen": "springgreen"},
            node2_connection={"seagreen": "darkgreen", "springgreen": "mediumspringgreen"},
        )
    ]
    + [
        SplitRule(
            name="var node chain duplication (two neighbors), step 2",
            input={"mediumseagreen": 1, "lightgreen": 1, "darkgreen": 1} | {p: 1 for p in parents},
            node1_connection={"mediumseagreen": "springgreen", "lightgreen": "lightgreen", "darkgreen": "darkgreen"}
            | {p: p for p in parents},
            node2_connection={},
        )
        for parents in NODE_PARENTS
    ]
    + [
        SplitRule(
            name="lambda duplication, step 2",
            input={"black": 1, "lightgreen": 1, "darkgreen": 1} | {p: 1 for p in parents},
            node1_connection={"black": "lightgray", "lightgreen": "green"} | {parents[0]: regular_color},
            node2_connection={"black": "darkgray", "darkgreen": "green"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["orange", "magenta"], "pink"),
            (["lightgray", "darkgray"], "black"),
            (["lightsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        SplitRule(
            name="app duplication",
            input={"red": 1, "blue": 1} | {p: 1 for p in parents},
            node1_connection={"red": "lightsalmon", "blue": "lightblue"} | {parents[0]: regular_color},
            node2_connection={"red": "salmon", "blue": "darkblue"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["orange", "magenta"], "pink"),
            (["lightgray", "darkgray"], "black"),
            (["lightsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        SplitRule(
            name="arg connector duplication",
            input={"navy": 1, "lightblue": 1, "darkblue": 1},
            node1_connection={"navy": "mediumblue", "lightblue": "blue"},
            node2_connection={"navy": "midnightblue", "darkblue": "blue"},
        ),
    ]
    + [
        # When cloning a variable where the lambda abstraction was also cloned, then we already have two var connector
        # nodes for this node that we cloned earlier
        SplitRule(
            name="var duplication (lambda term got cloned)",
            input={"springgreen": 1, "mediumspringgreen": 1} | {p: 1 for p in parents},
            node1_connection={"springgreen": "forestgreen"} | {parents[0]: regular_color},
            node2_connection={"mediumspringgreen": "forestgreen"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["orange", "magenta"], "pink"),
            (["lightgray", "darkgray"], "black"),
            (["lightsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        SplitRule(
            name="var duplication (lambda term got cloned, two neighbors)",
            input={"springgreen": 1, "mediumspringgreen": 1, "lightgreen": 1, "darkgreen": 1} | {p: 1 for p in parents},
            node1_connection={"springgreen": "forestgreen", "lightgreen": "green"} | {parents[0]: regular_color},
            node2_connection={"mediumspringgreen": "forestgreen", "darkgreen": "green"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["orange", "magenta"], "pink"),
            (["lightgray", "darkgray"], "black"),
            (["lightsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        # If the chain didn't get duplicated but the variable did, we need to create a new node in the chain.
        # We will do that as follows:
        # 1. Copy var node, connect both to previous var connector node. Connected each to one of the paerent nodes
        # 2. Var connector node creates new var connector node that connects the two var clones.
        # TODO: cloning while substitution
        SplitRule(
            name="var duplication (lambda term didn't get cloned)",
            input={"forestgreen": 1} | {p: 1 for p in parents},
            node1_connection={"forestgreen": "yellow"} | {parents[0]: regular_color},
            node2_connection={"forestgreen": "gold"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["orange", "magenta"], "pink"),
            (["lightgray", "darkgray"], "black"),
            (["lightsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        # TODO: cloning while substitution
        SplitRule(
            name="var duplication (lambda term didn't get cloned, two neighbors)",
            input={"forestgreen": 1, "green": 1} | {p: 1 for p in parents},
            node1_connection={"forestgreen": "yellow"} | {parents[0]: regular_color},
            node2_connection={"forestgreen": "gold", "green": "green"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["orange", "magenta"], "pink"),
            (["lightgray", "darkgray"], "black"),
            (["lightsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        SplitRule(
            name="connect duplicated var nodes",
            input={"yellow": 1, "gold": 1} | {p: 1 for p in parents},
            node1_connection={"yellow": "forestgreen"} | {p: p for p in parents},
            node2_connection={"yellow": "green", "gold": "forestgreen"},
        )
        for parents in [[], ["green"], ["seagreen"], ["pink", "fuchsia"]]
    ]
    # Deletion
    + [
        # When you have an application that tries to substitute into a lambda that has its bound variable not used
        # (no purple connection to the app node), then the application should delete the argument and pass the body of
        # the lambda to it's parent as is.
        # This is done by first creating a new deletion node connected to the argument and then doing the passing in
        # the second step.
        SplitRule(
            name="beta reduction (app), detect deletion step 1",
            input={"tan": 1, "blue": 1, "orangered": 1} | {p: 1 for p in parent},
            node1_connection={"orangered": "orangered", "tan": "tan"} | {p: p for p in parent},
            node2_connection={"blue": "maroon"},
        )
        for parent in NODE_PARENTS
    ]
    + [
        DeleteRule(
            name="beta reduction (app), detect deletion step 2",
            input={"orangered": 1, "tan": 1} | {p: 1 for p in parent},
            rewiring={("orangered", p): p for p in parent},
        )
        for parent in NODE_PARENTS
    ]
    + [
        DeleteRule(
            name="delete lambda, no bound variable",
            input={"black": 1, "maroon": 1},
            rewiring={("black", "maroon"): "maroon"},
        ),
        DeleteRule(
            name="delete lambda",
            input={"maroon": 1, "black": 1, "green": 1},
            rewiring={("black", "maroon"): "maroon"},
        ),
        DeleteRule(
            name="delete arg connecter",
            input={"maroon": 1, "navy": 1},
            rewiring={("navy", "maroon"): "maroon"},
        ),
        DeleteRule(
            name="delete application",
            input={"maroon": 1, "red": 1, "blue": 1},
            rewiring={("red", "maroon"): "maroon", ("blue", "maroon"): "maroon"},
        ),
        # When we delete a variable we want to also delete it's var connector node, but nothing that it is connected to.
        # For example if the variable is bound in a higher up lambda that is not being deleted, that lambda should be
        # left uptouched.
        # TODO: deletion while substitution
        # TODO: deletion while duplication
        DeleteRule(name="delete variable", input={"maroon": 1, "forestgreen": 1}, rewiring={}),
        DeleteRule(
            name="delete variable (two neighbor)",
            input={"maroon": 1, "forestgreen": 1, "green": 1},
            rewiring={("forestgreen", "green"): "olive"},
        ),
        DeleteRule(
            name="delete var connector (one neighbor)",
            input={"green": 1},
            rewiring={},
        ),
        DeleteRule(
            name="delete var connector (one neighbor) (2)",
            input={"olive": 1},
            rewiring={},
        ),
        DeleteRule(
            name="delete var connector (two neighbor)",
            input={"green": 1, "olive": 1},
            rewiring={("green", "olive"): "green"},
        ),
        DeleteRule(
            name="Delete singleton node",
            input={},
            rewiring={},
        ),
    ]
)
