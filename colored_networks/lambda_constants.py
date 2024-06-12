from colored_networks.lambda_calc import Abs, App, Var

id = Abs("x", Var("x"))
true = Abs("x", Abs("y", Var("x")))
false = Abs("x", Abs("y", Var("y")))
zero = Abs("f", Abs("x", Var("x")))
one = Abs("f", Abs("x", App(Var("f"), Var("x"))))
succ = Abs("n", Abs("f", Abs("x", App(Var("f"), App(App(Var("n"), Var("f")), Var("x"))))))


def num(n: int) -> Abs:
    inner = Var("x")
    for _ in range(n):
        inner = App(Var("f"), inner)
    return Abs("f", Abs("x", inner))


add = Abs("a", Abs("b", Abs("f", Abs("x", App(App(Var("a"), Var("f")), App(App(Var("b"), Var("f")), Var("x")))))))
mul = Abs("a", Abs("b", Abs("f", App(Var("a"), App(Var("b"), Var("f"))))))
