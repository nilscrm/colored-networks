from colored_networks.lambda_constants import zero, one, num, succ, add, mul, dec


def test_mul_1_1():
    mul_1_1 = mul(one, one)
    net = mul_1_1.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(one.to_colored_network())


def test_add_0_1():
    add_1_2 = add(zero, one)
    net = add_1_2.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(one.to_colored_network())


def mul_5_7():
    mul_5_7 = mul(num(5), num(7))
    net = mul_5_7.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(num(35).to_colored_network())


def test_succ_0():
    succ_0 = succ(zero)
    net = succ_0.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(one.to_colored_network())


def test_succ_num_2():
    succ_num_0 = succ(num(2))
    net = succ_num_0.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(num(3).to_colored_network())


def test_succ_13():
    succ_13 = succ(num(13))
    net = succ_13.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(num(14).to_colored_network())


def test_dec_0():
    dec_0 = dec(zero)
    net = dec_0.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(zero.to_colored_network())


def test_dec_1():
    dec_1 = dec(one)
    net = dec_1.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(zero.to_colored_network())


def test_dec_2():
    dec_2 = dec(num(2))
    net = dec_2.to_colored_network()
    net.reduce()
    assert net.seems_isomorphic_to(num(1).to_colored_network())


# def test_dec_3():
#     dec_3 = dec(num(3))
#     net = dec_3.to_colored_network()
#     net.reduce()
#     assert net.seems_isomorphic_to(num(2).to_colored_network())
