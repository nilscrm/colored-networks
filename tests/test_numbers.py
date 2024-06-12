from colored_networks.lambda_calc import App
from colored_networks.lambda_constants import add, mul, zero, one


def test_mul_1_1():
    mul_1_1 = App(App(mul, one), one)
    net = mul_1_1.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(one.to_colored_network())


def test_add_0_1():
    add_1_2 = App(App(add.clone(), zero), one)
    net = add_1_2.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(one.to_colored_network())
