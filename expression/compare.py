from typing import Any

from .binary import InfixBinaryOperator


@InfixBinaryOperator.decorate("=")
def equals(a: Any, b: Any) -> bool:
    return a == b

eq = equals


@InfixBinaryOperator.decorate("\u2260")
def not_equals(a: Any, b: Any) -> bool:
    return a != b

ne = not_equals


@InfixBinaryOperator.decorate("<")
def less_than(a: Any, b: Any) -> bool:
    return a < b

lt = less_than


@InfixBinaryOperator.decorate(">")
def greater_than(a: Any, b: Any) -> bool:
    return a > b

gt = greater_than


@InfixBinaryOperator.decorate("\u2264")
def less_than_or_equal_to(a: Any, b: Any) -> bool:
    return a <= b

le = less_than_or_equal_to


@InfixBinaryOperator.decorate("\u2265")
def greater_than_or_equal_to(a: Any, b: Any) -> bool:
    return a >= b

ge = greater_than_or_equal_to
