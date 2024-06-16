from colored_networks.lambda_calc import Abs, App, Var, LambdaTerm

id = Abs("x", Var("x"))
true = Abs("x", Abs("y", Var("x")))
false = Abs("x", Abs("y", Var("y")))

zero = Abs("f", Abs("x", Var("x")))
one = Abs("f", Abs("x", App(Var("f"), Var("x"))))
_succ = Abs("n", Abs("f", Abs("x", App(Var("f"), App(App(Var("n"), Var("f")), Var("x"))))))
_add = Abs("a", Abs("b", Abs("f", Abs("x", App(App(Var("a"), Var("f")), App(App(Var("b"), Var("f")), Var("x")))))))
_mul = Abs("a", Abs("b", Abs("f", App(Var("a"), App(Var("b"), Var("f"))))))


def succ(n: LambdaTerm) -> App:
    return App(_succ, n)


def add(a: LambdaTerm, b: LambdaTerm) -> App:
    return App(App(_add, a), b)


def mul(a: LambdaTerm, b: LambdaTerm) -> App:
    return App(App(_mul, a), b)


def num(n: int) -> Abs:
    inner = Var("x")
    for _ in range(n):
        inner = App(Var("f"), inner)
    return Abs("f", Abs("x", inner))


_pair = Abs("a", Abs("b", Abs("P", App(App(Var("P"), Var("a")), Var("b")))))
_fst = Abs("p", App(Var("p"), true))
_snd = Abs("p", App(Var("p"), false))


def pair(a: LambdaTerm, b: LambdaTerm) -> App:
    return App(App(_pair, a), b)


def fst(p: LambdaTerm) -> App:
    return App(_fst, p)


def snd(p: LambdaTerm) -> App:
    return App(_snd, p)


shift = Abs("p", Abs("P", App(App(Var("P"), App(Var("p"), false)), succ(App(Var("p"), true)))))
_dec = Abs("N", App(App(App(Var("N"), shift), pair(zero, zero)), true))


def dec(n: LambdaTerm) -> App:
    return App(_dec, n)
