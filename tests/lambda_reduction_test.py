from colored_networks.lambda_calc import Abs, App, Var

ID = Abs("x", Var("x"))
TRUE = Abs("x", Abs("y", Var("x")))
FALSE = Abs("x", Abs("y", Var("y")))


def test_id_id():
    id_id = App(ID.clone(), ID.clone())
    net = id_id.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(ID.to_colored_network())


def test_true_true_false():
    ttf = App(App(TRUE.clone(), TRUE.clone()), FALSE.clone())
    net = ttf.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(TRUE.to_colored_network())
