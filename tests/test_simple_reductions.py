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


def test_reduce_right_child():
    """Test (λx. x ((λy. y) x)) == λx. x x"""
    net = Abs("x", App(Var("x"), App(Abs("y", Var("y")), Var("x")))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", App(Var("x"), Var("x"))).to_colored_network())
