from expression import PrefixUnaryOperator
from .relation import Element, Relation


@PrefixUnaryOperator.decorate(name="elim")
def eliminate(relation: Relation) -> Relation:
    # we do it this way to preserve order
    elements: list[Element] = []
    seen: set[Element] = set()
    for element in relation.elements:
        if element in seen:
            continue
        elements.append(element)
        seen.add(element)
    return Relation(attributes=relation.attributes, elements=elements)

elim = eliminate
distinct = eliminate
unique = eliminate
