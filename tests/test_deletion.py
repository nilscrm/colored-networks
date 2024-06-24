from colored_networks.lambda_calc import Abs, App, Var
from colored_networks.lambda_constants import zero, one, num, id

def test_delete_abs():
    """ Test (λy. λx. x) id  == λx. x """
    net = App(Abs("y", Abs("x", Var("x"))), id).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", Var("x")).to_colored_network())


def test_delete_var():
    """ Test λx. (λy. x) x == λx. x """
    net = Abs("x", App(Abs("y", Var("x")), Var("x"))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", Var("x")).to_colored_network())

def test_delete_app():
    """ Test λx. (λy z. z) (x x) == λx. λz. z """
    net = Abs("x", App(Abs("y", Abs("z", Var("z"))), App(Var("x"), Var("x")))).to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("x", Abs("z", Var("z"))).to_colored_network())
