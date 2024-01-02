from expression import InfixBinaryOperator
from .relation import Relation


@InfixBinaryOperator.decorate(name="\u00d7")
def product(left_relation: Relation, right_relation: Relation) -> Relation:
    attributes = left_relation.attributes + right_relation.attributes
    elements = [
        left_element + right_element
        for left_element in left_relation.elements
        for right_element in right_relation.elements
    ]
    return Relation(attributes=attributes, elements=elements)

prod = product
times = product
X = product
x = product
