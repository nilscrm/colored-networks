from colored_networks.lambda_calc import Abs, App, Var
from colored_networks.lambda_constants import true, false, pair, fst, snd, shift, zero, one


def test_fst():
    """Test fst (pair true false) == true"""
    fst_pair = fst(pair(true, false))
    net = fst_pair.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(true.to_colored_network())


def test_snd():
    """Test snd (pair true false) == false"""
    snd_pair = snd(pair(true, false))
    net = snd_pair.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(false.to_colored_network())


def test_pair():
    """Test pair true false == pair true false"""
    pair_tf = pair(zero, zero)
    net = pair_tf.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(Abs("f", App(App(Var("f"), zero), zero)).to_colored_network())


def test_shift():
    """Test shift (pair 0 0) == pair 0 1"""
    shift_pair = App(shift, pair(zero, zero))
    net = shift_pair.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(pair(zero, one).to_colored_network().reduce())
