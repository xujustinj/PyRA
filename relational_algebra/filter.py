from typing import Any, Callable, Optional, TypeAlias, Union

from expression import InfixBinaryOperation
from .relation import Attribute, ConstantRelation, Element, Relation


ConditionArgument: TypeAlias = Union[int, ConstantRelation]
def get_argument_name(argument: ConditionArgument) -> str:
    if isinstance(argument, ConstantRelation):
        return argument.value
    assert isinstance(argument, int)
    if argument < 0:
        return f"#{-argument}\u2113"
    assert argument > 0
    return f"#{argument}"


Condition: TypeAlias = InfixBinaryOperation[
    ConditionArgument,
    ConditionArgument,
    bool,
]
def get_condition_name(condition: Condition) -> str:
    left_name = get_argument_name(condition.left_child.get())
    right_name = get_argument_name(condition.right_child.get())
    return f"{left_name}{condition.operator_name}{right_name}"


def resolve_argument(
        argument: ConditionArgument,
        left_relation: Optional[Relation] = None,
        right_relation: Optional[Relation] = None,
) -> tuple[Callable[[Element, Element], Any], Attribute]:
    resolve: Callable[[Element, Element], Any]
    if isinstance(argument, ConstantRelation):
        resolve = lambda l, r: argument.value
        attribute = argument.attribute
        return resolve, attribute
    else:
        assert argument != 0

        select: Callable[[Element, Element], Element]
        if argument < 0:
            argument = -argument
            name = f"#{argument}\u2113"
            relation = left_relation
            select = lambda l, r: l
        else:
            name = f"#{argument}"
            relation = right_relation
            select = lambda l, r: r

        assert relation is not None
        A = relation.num_attributes
        assert 0 < argument <= A, \
            f"index #{name} out of bounds (max {A})"
        index = argument - 1
        resolve = lambda l, r: select(l, r)[index]
        attribute = relation.attributes[index]

    return resolve, attribute
