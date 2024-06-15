from colored_networks.lambda_calc import Abs, App, Var
from colored_networks.lambda_constants import id, true, false


def test_id_id():
    """Test (λx. x) (λx. x) == λx. x"""
    id_id = App(id, id)
    net = id_id.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(id.to_colored_network())


def test_true_true_false():
    """Test (λx y. x) (λx y. x) (λx y. y) == λx y. x"""
    ttf = App(App(true, true), false)
    net = ttf.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(true.to_colored_network())


def test_id_dup():
    """Test (λx. x x) (λx. x) == λx. x"""
    id_dup = App(Abs("x", App(Var("x"), Var("x"))), id)
    net = id_dup.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(id.to_colored_network())


def test_reduce_right_child():
    """Test (λx. x ((λy. y) x)) == λx. x x"""
    net = Abs("x", App(Var("x"), App(Abs("y", Var("y")), Var("x")))).to_colored_network()
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
