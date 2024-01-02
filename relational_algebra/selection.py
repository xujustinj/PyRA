from typing import Union

from expression import PrefixUnaryOperator
from .filter import Condition, get_condition_name, resolve_argument
from .relation import Relation


class Select:
    def __getitem__(
            self,
            cond: Union[Condition, tuple[Condition, ...]],
    ) -> PrefixUnaryOperator[Relation, Relation]:
        conditions = list(cond) if isinstance(cond, tuple) else [cond]
        name = f"\u03c3[{','.join(get_condition_name(c) for c in conditions)}]"

        def _select(relation: Relation) -> Relation:
            call_name = f"{name} {relation}"

            converged: bool = False
            while not converged:
                """
                If the condition is of the form A = B, then we know that the
                only remaining values in attributes A and B belong to the type
                intersection A & B.

                Later, if there is another condition B = C, then we can also
                transitively deduce that A = C. At the moment, this is handled
                rather naively by simply running type deduction in a loop until
                convergence.
                """
                converged = True
                for k, condition in enumerate(conditions):
                    condition_name = f"{call_name} condition #{k+1} ({get_condition_name(condition)})"
                    l = condition.left_child.get()
                    r = condition.right_child.get()
                    assert isinstance(l, int) or isinstance(r, int)

                    try:
                        lhs, la = resolve_argument(l, right_relation=relation)
                        rhs, ra = resolve_argument(r, right_relation=relation)
                    except Exception as e:
                        e.args = (f"{condition_name}:", *e.args)
                        raise

                    if condition.operator_name == "=":
                        a = la & ra
                        assert len(a) > 0, \
                            f"{condition_name}: incompatible types {la} versus {ra}"
                        if len(a) < len(la) and isinstance(l, int):
                            converged = False
                            relation = relation.replace_attribute(index=l-1, attribute=a)
                        if len(a) < len(ra) and isinstance(r, int):
                            converged = False
                            relation = relation.replace_attribute(index=r-1, attribute=a)

                    relation = relation.filter_elements(
                        lambda element: condition.f(lhs((), element), rhs((), element))
                    )

            return relation

        return PrefixUnaryOperator(_select, name=name)

select = Select()
sigma = select
