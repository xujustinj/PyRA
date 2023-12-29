"""
https://tomerfiliba.com/blog/Infix-Operators
oh my goodness this is amazing
"""

from abc import ABC, abstractmethod
from functools import cache, cached_property
from typing import Any, Callable, Generic, Optional, TypeVar, Union

L = TypeVar("L", contravariant=True)
R = TypeVar("R", contravariant=True)
T = TypeVar("T", covariant=True)

class Expression(ABC, Generic[T]):
    @property
    @abstractmethod
    def rootname(self) -> str:
        pass

    @property
    @abstractmethod
    def fullname(self) -> str:
        pass

    @property
    def left_children(self) -> tuple["Expression[Any]", ...]:
        return ()

    @property
    def right_children(self) -> tuple["Expression[Any]", ...]:
        return ()

    @cached_property
    def children(self) -> tuple["Expression[Any]", ...]:
        return (*self.left_children, *self.right_children)

    @property
    def has_children(self) -> bool:
        return len(self.children) > 0

    @property
    def is_infix(self) -> bool:
        return len(self.left_children) > 0 and len(self.right_children) > 0

    @abstractmethod
    def get(self) -> T:
        pass

    def __str__(self) -> str:
        return self.fullname

class Constant(Expression[T]):
    def __init__(self, value: T, name: Optional[str] = None):
        self.value = value
        self.name = str(value) if name is None else name

    @property
    def rootname(self) -> str:
        return self.name

    @property
    def fullname(self) -> str:
        return self.name

    def get(self) -> T:
        return self.value

Value = Union[Expression[T], T]
def as_expression(value: Value[T]) -> Expression[T]:
    return value if isinstance(value, Expression) else Constant(value)
