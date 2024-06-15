from colored_networks.lambda_calc import App
from colored_networks.lambda_constants import true, false, num, pair, fst, snd, shift


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


def test_shift():
    """Test shift (pair 0 0) == pair 0 1"""
    shift_pair = App(shift, pair(num(0), num(0)))
    net = shift_pair.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(pair(num(0), num(1)).to_colored_network())
