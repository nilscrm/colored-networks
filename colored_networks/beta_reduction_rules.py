from colored_networks.colored_network import SplitRule, DeleteRule

"""
Meaning of the colors

black: body of a lambda abstraction
lightgray/darkgray: connects duplicated lambda terms to their not yet duplicated child
red: function of an application
lighsalmon/salmon: connects duplicated app nodes to their not yet duplicated left child
coral: connects application node to lambda function after lambda function has produced indicator node for app node
orangered: left child of application after lambda node was removed from it
tomato: connect app node and dup node that has just been maked with fuchsia.
    Next the app node should remove itself to let the dup node copy the argument.

blue: argument of an application
lighblue/darkblue: connects duplicated app nodes to their not yet duplicated right child
navy: parent node (this node is argument of an application)
mediumblue/midnightblue: connects duplicated connecter nodes to their not yet duplicated child
cornflowerblue: prepare right child for substitution
slateblue: right child about to be substituted

green/forestgreen: Chain of dup nodes from lambda abstraction, they always have a connector node between then,
    the parent connected with forestgreen and the child connected with green
seagreen/mediumseagreen: Chain on dup nodes that should be duplicated
springgreen/mediumspringgreen: Connectes duplicated dup nodes to their not yet duplicated parent dup node
lighgreen/darkgreen: Connect duplicated lambda nodes to their not yet duplicated dup node

yellow: Variable duplicator node binds
goldenrod/darkgoldenrod: Connectes duplicated dup nodes from duplicated chain to not yet duplicated variable node
lightyellow/khaki: Connect duplicated variable to their not yet duplicated dup node
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
        # beta reduction (lambda)
        SplitRule(
            name="beta reduction (lambda), bound variable not used, step 1",
            input={"black": 1, "red": 1},
            node1_connection={"black": "black", "red": "coral"},
            node2_connection={"red": "tan"},
        ),
        DeleteRule(
            name="beta reduction (lambda), bound variable not used, step 2",
            input={"black": 1, "coral": 1},
            rewiring={("black", "coral"): "orangered"},
        ),
        SplitRule(
            name="beta reduction (lambda), step 1",
            input={"black": 1, "red": 1, "green": 1},
            node1_connection={"black": "black", "red": "coral", "green": "green"},
            node2_connection={"red": "tan"},
        ),
        DeleteRule(
            name="beta reduction (lambda), step 2",
            input={"coral": 1, "black": 1, "green": 1},
            rewiring={("coral", "green"): "purple", ("black", "coral"): "orangered"},
        ),
    ]
    + [
        SplitRule(
            name="beta reduction (app) step 1",
            input={"tan": 1, "purple": 1, "blue": 1, "orangered": 1} | {p: 1 for p in parent},
            node1_connection={"tan": "tan", "purple": "purple", "orangered": "orangered", "blue": "cornflowerblue"}
            | {p: p for p in parent},
            node2_connection={},
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
            input={"tan": 1, "purple": 1, "slateblue": 1, "orangered": 1} | {p: 1 for p in parent},
            node1_connection={"purple": "fuchsia"},
            node2_connection={"tan": "tan", "purple": "purple", "orangered": "tomato", "slateblue": "slateblue"}
            | {p: p for p in parent},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        DeleteRule(
            name="beta reduction (app) step 3",
            input={"tan": 1, "purple": 1, "slateblue": 1, "tomato": 1} | {p: 1 for p in parent},
            rewiring={("purple", "slateblue"): "pink"} | {("tomato", p): p for p in parent},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        # Variable substitution
        DeleteRule(
            name="dup node connecter, substitution propagation propagation",
            input={"pink": 1, "fuchsia": 1, "forestgreen": 1},
            rewiring={("forestgreen", "fuchsia"): "fuchsia", ("pink", "forestgreen"): "pink"},
        ),
        DeleteRule(
            name="var substitution (dup)",
            input={"pink": 1, "fuchsia": 1, "yellow": 1},
            rewiring={("pink", "yellow"): "lime"},
        ),
        # If variable was bound to multiple variables we need to clone the argument to substitute the term into
        # multiple variables.
        DeleteRule(
            name="detect argument duplication",
            input={"pink": 1, "yellow": 1, "green": 1, "fuchsia": 1},
            rewiring={
                # Mark next dup node ready for duplication
                ("fuchsia", "green"): "fuchsia",
                # Connect term to variable to be substitued for. Use orange instead of lime to wait for node to be
                # duplicated.
                ("pink", "yellow"): "orange",
                # Connect term to next to node. Use magenta instead of pink to wait for node to be duplicated.
                ("pink", "green"): "magenta",
            },
        ),
        # -- Root node duplication --
        # Once the node duplication has been detected, we need first need to clone the root node.
        # After that every child node will have 2 parents and thus detect that it needs to clone itself.
        SplitRule(
            name="lambda root duplication, bound variable not used",
            input={"black": 1, "orange": 1, "magenta": 1},
            node1_connection={"black": "lightgray", "orange": "lime"},
            node2_connection={"black": "darkgray", "magenta": "pink"},
        ),
        # When duplicating a lambda term, first duplicate the entire chain of dup nodes that bind this variable.
        # The reason for this is that when a variable is cloned we need to know whether the lambda that binds this
        # variable was also cloned or not. By first cloning the dup node chain we know this.
        SplitRule(
            name="lambda root duplication, step 1",
            input={"black": 1, "green": 1, "orange": 1, "magenta": 1},
            node1_connection={"black": "black", "green": "seagreen", "orange": "orange", "magenta": "magenta"},
            node2_connection={},
        ),
        SplitRule(
            name="lambda root duplication, step 2",
            input={"black": 1, "springgreen": 1, "mediumspringgreen": 1, "orange": 1, "magenta": 1},
            node1_connection={"black": "lightgray", "springgreen": "green", "orange": "lime"},
            node2_connection={"black": "darkgray", "mediumspringgreen": "green", "magenta": "pink"},
        ),
        SplitRule(
            name="app root duplication",
            input={"red": 1, "blue": 1, "orange": 1, "magenta": 1},
            node1_connection={"red": "lighsalmon", "blue": "lighblue", "orange": "lime"},
            node2_connection={"red": "salmon", "blue": "darkblue", "magenta": "pink"},
        ),
        SplitRule(
            name="var root duplication",
            input={"yellow": 1, "orange": 1, "magenta": 1},
            node1_connection={"yellow": "lightyellow", "orange": "lime"},
            node2_connection={"yellow": "khaki", "magenta": "pink"},
        ),
    ]
    # The following duplication happens because the node realizes it has two parents.
    + [
        SplitRule(
            name="lambda duplication, bound variable not used",
            input={"black": 1} | {p: 1 for p in parents},
            node1_connection={"black": "lightgray"} | {parents[0]: regular_color},
            node2_connection={"black": "darkgray"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["lightgray", "darkgray"], "black"),
            (["lighsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        # When duplicating a lambda term, first duplicate the entire chain of dup nodes that bind this variable.
        # The reason for this is that when a variable is cloned we need to know whether the lambda that binds this
        # variable was also cloned or not. By first cloning the dup node chain we know this.
        SplitRule(
            name="lambda duplication, step 1",
            input={"black": 1, "green": 1} | {p: 1 for p in parents},
            node1_connection={"black": "lightgray", "green": "lightgreen"} | {parents[0]: regular_color},
            node2_connection={"black": "darkgray", "green": "darkgreen"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["lightgray", "darkgray"], "black"),
            (["lighsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        SplitRule(
            name="app duplication",
            input={"red": 1, "blue": 1} | {p: 1 for p in parents},
            node1_connection={"red": "lighsalmon", "blue": "lighblue"} | {parents[0]: regular_color},
            node2_connection={"red": "salmon", "blue": "darkblue"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["lightgray", "darkgray"], "black"),
            (["lighsalmon", "salmon"], "red"),
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
        SplitRule(
            name="var duplication (lambda term didn't get cloned)",
            input={"yellow": 1} | {p: 1 for p in parents},
            node1_connection={"yellow": "lightyellow"} | {parents[0]: regular_color},
            node2_connection={"yellow": "khaki"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["lightgray", "darkgray"], "black"),
            (["lighsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        SplitRule(
            name="var duplication (lambda term got cloned)",
            input={"goldenrod": 1, "darkgoldenrod": 1} | {p: 1 for p in parents},
            node1_connection={"goldenrod": "yellow"} | {parents[0]: regular_color},
            node2_connection={"darkgoldenrod": "yellow"} | {parents[1]: regular_color},
        )
        for (parents, regular_color) in [
            (["lightgray", "darkgray"], "black"),
            (["lighsalmon", "salmon"], "red"),
            (["mediumblue", "midnightblue"], "navy"),
        ]
    ]
    + [
        # Go down dup node chain and mark nodes for duplciation
        SplitRule(
            name="dup connector node chain duplication, step 1",
            input={"seagreen": 1, "forestgreen": 1},
            node1_connection={"seagreen": "seagreen", "forestgreen": "mediumseagreen"},
            node2_connection={},
        ),
        SplitRule(
            name="dup node chain duplication, step 1",
            input={"mediumseagreen": 1, "yellow": 1, "green": 1},
            node1_connection={"mediumseagreen": "mediumseagreen", "yellow": "yellow", "green": "seagreen"},
            node2_connection={},
        ),
        # Once last dup node in the chain has been reached, start with duplicating the dup nodes.
        SplitRule(
            name="dup node chain duplication (one neighbors), step 2",
            input={"mediumseagreen": 1, "yellow": 1},
            node1_connection={"mediumseagreen": "springgreen", "yellow": "goldenrod"},
            node2_connection={"mediumseagreen": "mediumspringgreen", "yellow": "darkgoldenrod"},
        ),
        # Go up the dup node chain and duplicate the nodes
        SplitRule(
            name="dup connector node chain duplication, step 2",
            input={"seagreen": 1, "springgreen": 1, "mediumspringgreen": 1},
            node1_connection={"seagreen": "springgreen", "springgreen": "forestgreen"},
            node2_connection={"seagreen": "mediumspringgreen", "mediumspringgreen": "forestgreen"},
        ),
        SplitRule(
            name="dup node chain duplication (two neighbors), step 2",
            input={"mediumseagreen": 1, "yellow": 1, "springgreen": 1, "mediumspringgreen": 1},
            node1_connection={"mediumseagreen": "springgreen", "yellow": "goldenrod", "springgreen": "green"},
            node2_connection={
                "mediumseagreen": "mediumspringgreen",
                "yellow": "darkgoldenrod",
                "mediumspringgreen": "green",
            },
        ),
        # If the chain didn't get duplicated but the variable did, we need to create a new node in the chain.
        SplitRule(
            name="dup node duplication (one neighbor), step 1",
            input={"forestgreen": 1, "lighyellow": 1, "khaki": 1},
            node1_connection={"forestgreen": "forestgreen", "lighyellow": "lightyellow"},
            node2_connection={"khaki": "yellow", "lighyellow": "gold"},
        ),
        SplitRule(
            name="dup node duplication (two neighbors), step 1",
            input={"forestgreen": 1, "green": 1, "lighyellow": 1, "khaki": 1},
            node1_connection={"forestgreen": "forestgreen", "lighyellow": "lightyellow"},
            node2_connection={"green": "green", "khaki": "yellow", "lighyellow": "gold"},
        ),
    ]
    + [
        # Insert new dup connector node between the two duplicated dup nodes
        SplitRule(
            name="dup node duplication, step 2",
            input={"lightyellow": 1, "gold": 1} | {p: 1 for p in parent},
            node1_connection={"lightyellow": "yellow"} | {p: p for p in parent},
            node2_connection={"lightyellow": "olive", "green": "forestgreen"},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        DeleteRule(
            name="var substitution",
            input={"lime": 1} | {p: 1 for p in parent},
            rewiring={(p, "lime"): p for p in parent},
        )
        # marron if the variable should be deleted, then this gets propagated to the substitution term
        for parent in [[], ["black"], ["red"], ["navy"], ["marron"]]
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
        for parent in [[], ["black"], ["red"], ["navy"]]
    ]
    + [
        DeleteRule(
            name="beta reduction (app), detect deletion step 2",
            input={"orangered": 1, "tan": 1} | {p: 1 for p in parent},
            rewiring={("orangered", p): p for p in parent},
        )
        for parent in [[], ["black"], ["red"], ["navy"]]
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
        # When we delete a variable we want to also delete it's duplicator node, but nothing that it is connected to.
        # For example if the variable is bound in a higher up lambda that is not being deleted, that lambda should be
        # left uptouched.
        SplitRule(
            name="delete variable",
            input={"maroon": 1, "yellow": 1},
            node1_connection={"yellow": "darkred"},
            node2_connection={},
        ),
        DeleteRule(
            name="delete dup node",
            input={"darkred": 1},
            rewiring={},
        ),
        DeleteRule(
            name="delete dup node (one neighbor)",
            input={"darkred": 1, "forestgreen": 1},
            rewiring={("darkred", "forestgreen"): "firebrick"},
        ),
        DeleteRule(
            name="delete dup node (sandwiched)",
            input={"darkred": 1, "green": 1, "forestgreen": 1},
            rewiring={("darkred", "forestgreen"): "firebrick", ("forestgreen", "green"): "forestgreen"},
        ),
        DeleteRule(
            name="delete dup connector node (no neighbor)",
            input={"firebrick": 1},
            rewiring={},
        ),
        DeleteRule(
            name="delete dup connector node (one neighbor)",
            input={"firebrick": 1, "green": 1},
            rewiring={},
        ),
        DeleteRule(
            name="delete dup connector node (two neighbors)",
            input={"firebrick": 1, "green": 1, "forestgreen": 1},
            rewiring={("forestgreen", "green"): "green"},
        ),
        DeleteRule(
            name="Delete singleton node",
            input={},
            rewiring={},
        ),
    ]
)
