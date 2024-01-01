from typing import Callable, Generic, TypeVar
from functools import cached_property

from .expression import Expression, as_expression, Value

L = TypeVar("L", contravariant=True)
R = TypeVar("R", contravariant=True)
T = TypeVar("T", covariant=True)


class InfixBinaryOperation(Expression[T], Generic[L, R, T]):
    def __init__(
            self,
            f: Callable[[L, R], T],
            operator_name: str,
            left_child: Value[L],
            right_child: Value[R],
    ):
        self.f = f
        self.operator_name = operator_name
        self.left_child = as_expression(left_child)
        self.right_child = as_expression(right_child)

    @property
    def rootname(self) -> str:
        return self.operator_name

    @property
    def fullname(self) -> str:
        return f"{self.left_child.fullname} {self.operator_name} {self.right_child.fullname}"

    @property
    def left_children(self) -> tuple[Expression[L]]:
        return (self.left_child,)

    @property
    def right_children(self) -> tuple[Expression[R]]:
        return (self.right_child,)

    def get(self) -> T:
        return self._value

    @cached_property
    def _value(self) -> T:
        return self.f(self.left_child.get(), self.right_child.get())


class LeftPartialInfixBinaryOperator(Generic[L, R, T]):
    def __init__(
            self,
            f: Callable[[L, R], T],
            operator_name: str,
            left_child: Value[L],
    ):
        self.f = f
        self.operator_name = operator_name
        self.left_child = left_child

    def __or__(self, right_child: Value[R]) -> InfixBinaryOperation[L, R, T]:
        return InfixBinaryOperation(
            self.f,
            operator_name=self.operator_name,
            left_child=self.left_child,
            right_child=right_child,
        )

class RightPartialInfixBinaryOperator(Generic[L, R, T]):
    def __init__(
            self,
            f: Callable[[L, R], T],
            operator_name: str,
            right_child: Value[R],
    ):
        self.f = f
        self.operator_name = operator_name
        self.right_child = right_child

    def __ror__(self, left_child: Value[L]) -> InfixBinaryOperation[L, R, T]:
        return InfixBinaryOperation(
            self.f,
            operator_name=self.operator_name,
            left_child=left_child,
            right_child=self.right_child,
        )

class InfixBinaryOperator(Generic[L, R, T]):
    def __init__(
            self,
            f: Callable[[L, R], T],
            name: str,
    ):
        self.f = f
        self.name = name

    def __or__(self, right_child: Value[R]) -> RightPartialInfixBinaryOperator[L, R, T]:
        return RightPartialInfixBinaryOperator(
            self.f,
            operator_name=self.name,
            right_child=right_child,
        )

    def __ror__(self, left_child: Value[L]) -> LeftPartialInfixBinaryOperator[L, R, T]:
        return LeftPartialInfixBinaryOperator(
            self.f,
            operator_name=self.name,
            left_child=left_child,
        )

    def __call__(self, right_child: Value[R]) -> RightPartialInfixBinaryOperator[L, R, T]:
        return RightPartialInfixBinaryOperator(
            self.f,
            operator_name=self.name,
            right_child=right_child,
        )

    @classmethod
    def decorate(cls, name: str) -> Callable[
        [Callable[[L, R], T]],
        "InfixBinaryOperator[L, R, T]",
    ]:
        return lambda f: cls(f, name=name)
