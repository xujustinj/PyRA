from typing import Union

from expression import InfixBinaryOperator
from .filter import Condition, get_condition_name, resolve_argument
from .relation import Relation


class Join:
    def __getitem__(
            self,
            cond: Union[Condition, tuple[Condition, ...]],
    ) -> InfixBinaryOperator[Relation, Relation, Relation]:
        conditions = list(cond) if isinstance(cond, tuple) else [cond]
        name = f"\u00d7 \u03c3[{','.join(get_condition_name(c) for c in conditions)}]"

        def _join(left_relation: Relation, right_relation: Relation) -> Relation:
            call_name = f"{left_relation} {name} {right_relation}"
            element_pairs = [
                (left_element, right_element)
                for left_element in left_relation.elements
                for right_element in right_relation.elements
            ]

            converged: bool = False
            while not converged:
                converged = True
                for c, condition in enumerate(conditions):
                    condition_name = f"{call_name} condition #{c+1} ({get_condition_name(condition)})"
                    l = condition.left_child.get()
                    r = condition.right_child.get()
                    assert isinstance(l, int) or isinstance(r, int)

                    try:
                        lhs, la = resolve_argument(l, left_relation, right_relation)
                        rhs, ra = resolve_argument(r, left_relation, right_relation)
                    except Exception as e:
                        e.args = (f"{condition_name}:", *e.args)
                        raise

                    if condition.operator_name == "=":
                        a = la & ra
                        assert len(a) > 0, \
                            f"{condition_name}: incompatible types {la} versus {ra}"
                        if len(a) < len(la) and isinstance(l, int):
                            converged = False
                            if l < 0:
                                left_relation = left_relation.replace_attribute(index=-l-1, attribute=a)
                            else:
                                assert l > 0
                                right_relation = right_relation.replace_attribute(index=l-1, attribute=a)
                        if len(a) < len(ra) and isinstance(r, int):
                            converged = False
                            if r < 0:
                                left_relation = left_relation.replace_attribute(index=-r-1, attribute=a)
                            else:
                                assert r > 0
                                right_relation = right_relation.replace_attribute(index=r-1, attribute=a)

                    element_pairs = list(filter(
                        lambda pair: condition.f(lhs(*pair), rhs(*pair)),
                        element_pairs,
                    ))

            attributes = left_relation.attributes + right_relation.attributes
            return Relation(attributes=attributes, elements=[
                left_element + right_element
                for left_element, right_element in element_pairs
            ])

        return InfixBinaryOperator(_join, name=name)

join = Join()
