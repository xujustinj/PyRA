from typing import Callable, Generic, TypeVar
from functools import cache, cached_property

from .expression import Expression, as_expression, Value

R = TypeVar("R", contravariant=True)
T = TypeVar("T", covariant=True)


class PrefixUnaryOperation(Expression[T], Generic[R, T]):
    def __init__(
            self,
            f: Callable[[R], T],
            operator_name: str,
            right_child: Value[R],
    ):
        self.f = f
        self.operator_name = operator_name
        self.right_child = as_expression(right_child)

    @property
    def rootname(self) -> str:
        return self.operator_name

    @cached_property
    def fullname(self) -> str:
        return f"{self.operator_name} {self.right_child.fullname}"

    @cached_property
    def right_children(self) -> tuple[Expression[R]]:
        return (self.right_child,)

    @cache
    def get(self) -> T:
        return self.f(self.right_child.get())


class PrefixUnaryOperator(Generic[R, T]):
    def __init__(self, f: Callable[[R], T], name: str):
        self.f = f
        self.name = name

    def __call__(self, right_child: Value[R]) -> PrefixUnaryOperation[R, T]:
        return PrefixUnaryOperation(
            self.f,
            operator_name=self.name,
            right_child=right_child,
        )

    def __or__(self, right_child: Value[R]) -> PrefixUnaryOperation[R, T]:
        return self(right_child)

    @classmethod
    def decorate(cls, name: str) -> Callable[
        [Callable[[R], T]],
        "PrefixUnaryOperator[T]",
    ]:
        return lambda f: cls(f, name=name)
