from expression import InfixBinaryOperator
from .relation import Relation


@InfixBinaryOperator.decorate(name="\u222a")
def union(left_relation: Relation, right_relation: Relation) -> Relation:
    name = f"{left_relation} \u222a {right_relation}"

    lA = left_relation.num_attributes
    rA = right_relation.num_attributes
    assert lA == rA, \
        f"{name} : relations have different arities ({lA} versus {rA})"

    attributes = tuple(la | ra for la, ra in zip(left_relation.attributes, right_relation.attributes))
    elements = left_relation.elements + right_relation.elements

    return Relation(attributes=attributes, elements=elements)

U = union
u = union
