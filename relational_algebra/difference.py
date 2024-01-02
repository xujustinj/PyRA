from expression import InfixBinaryOperator
from .relation import Relation


@InfixBinaryOperator.decorate(name="\u2212")
def difference(left_relation: Relation, right_relation: Relation) -> Relation:
    name = f"{left_relation} \u2212 {right_relation}"

    lA = left_relation.num_attributes
    rA = right_relation.num_attributes
    assert lA == rA, \
        f"{name} : relations have different arities ({lA} versus {rA})"

    for i, (la, ra) in enumerate(zip(left_relation.attributes, right_relation.attributes)):
        assert len(la & ra) > 0, \
            f"{name} : incompatible types at index {i+1}: {la} versus {ra}"

    exclude = set(right_relation.elements)
    elements = left_relation.filter_elements(lambda element: element not in exclude).elements

    return Relation(attributes=left_relation.attributes, elements=elements)

subtract = difference
minus = difference
