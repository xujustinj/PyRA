from . import eq, InfixBinaryOperator, PrefixUnaryOperator, resolve

@PrefixUnaryOperator.decorate("-")
def negate(a: int) -> int:
    return -a

@InfixBinaryOperator.decorate("+")
def plus(a: int, b: int) -> int:
    return a + b

@InfixBinaryOperator.decorate("\u00d7")
def times(a: int, b: int) -> int:
    return a * b

assert resolve((1 |plus| negate(2) |times| 3) |eq| -3)
