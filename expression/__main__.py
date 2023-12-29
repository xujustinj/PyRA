from . import PrefixUnaryOperator, InfixBinaryOperator, resolve

@PrefixUnaryOperator.decorate("-")
def negate(a: int) -> int:
    return -a

@InfixBinaryOperator.decorate("+")
def plus(a: int, b: int) -> int:
    return a + b

@InfixBinaryOperator.decorate("\u00d7")
def times(a: int, b: int) -> int:
    return a * b

resolve(1 |plus| negate(2) |times| 3)
