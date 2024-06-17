from colored_networks.lambda_calc import Abs, App, Var
from colored_networks.lambda_constants import id


def test_id_dup():
    """Test (λx. x x) (λx. x) == λx. x"""
    id_dup = App(Abs("x", App(Var("x"), Var("x"))), id)
    net = id_dup.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(id.to_colored_network())


def test_dup_nested_fun():
    """Test ((λx. x x) (λx y. y)) == λy. y"""
    net = App(Abs("x", App(Var("x"), Var("x"))), Abs("x", Abs("y", Var("y")))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("y", Var("y")).to_colored_network())


def test_dup_nested_fun2():
    """Test ((λx. x x) (λx y z. y z z)) == λy z. y z z"""
    net = App(
        Abs("x", App(Var("x"), Var("x"))), Abs("x", Abs("y", Abs("z", App(Var("y"), App(Var("z"), Var("z"))))))
    ).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("y", Abs("z", App(Var("y"), App(Var("z"), Var("z"))))).to_colored_network())


def test_dup_duplicating_term():
    """Test ((λx. x x) (id id)) == id"""
    net = App(Abs("y", App(Var("y"), Var("y"))), App(id, id)).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(id.to_colored_network())


def test_dup_bound_var():
    """Test (λx. (λy. y y) x) == λx. x x"""
    net = Abs("x", App(Abs("y", App(Var("y"), Var("y"))), Var("x"))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), Var("x"))).to_colored_network())


def test_dup_first_in_chain():
    """Test (λx. (λy. y y) x x) == λx. x x x"""
    net = Abs("x", App(App(Abs("y", Var("y")), Var("x")), Var("x"))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), Var("x"))).to_colored_network())


def test_dup_middle_in_chain1():
    """Test (λx. x ((λy. y y) x x)) == λx. x x x x"""
    net = Abs("x", App(Var("x"), App(Abs("y", Var("y")), App(Var("x"), Var("x"))))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), App(Var("x"), Var("x")))).to_colored_network())


def test_dup_middle_in_chain2():
    """Test (λx. x x ((λy. y y) x x)) == λx. x x x x x"""
    net = Abs("x", App(Var("x"), App(Var("x"), App(Abs("y", Var("y")), App(Var("x"), Var("x")))))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), App(Var("x"), App(Var("x"), Var("x"))))).to_colored_network())


def test_dup_last_in_chain1():
    """Test (λx. x ((λy. y y) x)) == λx. x x x"""
    net = Abs("x", App(Var("x"), App(Abs("y", Var("y")), Var("x")))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), Var("x"))).to_colored_network())


def test_dup_last_in_chain2():
    """Test (λx. x x ((λy. y y) x)) == λx. x x x x"""
    net = Abs("x", App(Var("x"), App(Var("x"), App(Abs("y", Var("y")), Var("x"))))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), App(Var("x"), Var("x")))).to_colored_network())


def test_dup_bound_variable1():
    """Test (λx. (λy. y y) x) == λx. x x"""
    net = Abs("x", App(Abs("y", App(Var("y"), Var("y"))), Var("x"))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), Var("x"))).to_colored_network())


def test_dup_bound_variable2():
    """Test (λx. x ((λy. y y) x) x) == λx. x (x x) x"""
    net = Abs(
        "x",
        App(
            Var("x"),
            App(
                App(
                    Abs("y", App(Var("y"), Var("y"))),
                    Var("x"),
                ),
                Var("x"),
            ),
        ),
    ).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(App(Var("x"), App(Var("x"), Var("x"))), Var("x"))).to_colored_network())


def test_dup_bound_variable3():
    """Test (λx. x x ((λy. y y) x)) == λx. x x (x x)"""
    net = Abs(
        "x",
        App(
            App(Var("x"), Var("x")),
            App(Abs("y", App(Var("y"), Var("y"))), Var("x")),
        ),
    ).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(App(Var("x"), Var("x")), App(Var("x"), Var("x")))).to_colored_network())


def test_dup_bound_variable4():
    """Test (λx. x ((λy. y y) x) ((λy. y y) x) x) == λx. x (x x) (x x) x"""
    net = Abs(
        "x",
        App(
            App(
                App(
                    Var("x"),
                    App(Abs("y", App(Var("y"), Var("y"))), Var("x")),
                ),
                App(Abs("y", App(Var("y"), Var("y"))), Var("x")),
            ),
            Var("x"),
        ),
    ).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(
        Abs(
            "x",
            App(
                App(
                    App(
                        Var("x"),
                        App(Var("x"), Var("x")),
                    ),
                    App(Var("x"), Var("x")),
                ),
                Var("x"),
            ),
        ).to_colored_network()
    )
