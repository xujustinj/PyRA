from typing import Any, Callable, Iterable, TypeAlias


class Attribute:
    types: frozenset[str]

    def __init__(self, *types: str):
        self.types = frozenset(types)

    def __str__(self) -> str:
        return "|".join(self.types)

    def __len__(self) -> int:
        return len(self.types)

    def __and__(self, other: "Attribute") -> "Attribute":
        return Attribute(*(self.types & other.types))

    def __or__(self, other: "Attribute") -> "Attribute":
        return Attribute(*(self.types | other.types))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Attribute) and self.types == other.types


Element: TypeAlias = tuple[Any, ...]

class Relation:
    attributes: tuple[Attribute, ...]
    elements: tuple[Element, ...]

    def __init__(
            self,
            attributes: tuple[Attribute, ...],
            elements: Iterable[Element],
    ):
        assert len(attributes) > 0
        assert all(len(a) > 0 for a in attributes)
        self.attributes = attributes

        for element in elements:
            assert len(element) == len(attributes)
        self.elements = tuple(elements)

    def __str__(self) -> str:
        return f"( {' , '.join(str(a) for a in self.attributes)} )"

    def __repr__(self) -> str:
        if self.num_elements == 0:
            return str(self)
        widths = tuple(
            max(
                len(str(self.attributes[i])),
                max(len(str(element[i])) for element in self.elements)
            )
            for i in range(self.num_attributes)
        )
        s = f"( {' , '.join(str(a).ljust(w) for a, w in zip(self.attributes, widths))} )"
        for element in self.elements:
            s += f"\n  {' , '.join(str(v).ljust(w) for v, w in zip(element, widths))}"
        return s

    @property
    def num_attributes(self) -> int:
        return len(self.attributes)

    @property
    def num_elements(self) -> int:
        return len(self.elements)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Relation)
            and self.attributes == other.attributes
            and sorted(self.elements) == sorted(other.elements)
        )

    def replace_attribute(self, index: int, attribute: Attribute) -> "Relation":
        """
        Returns a relation where the attribute at index i is replaced with a.
        Generally useful for changing the type of a column.
        """
        attributes = (*self.attributes[:index], attribute, *self.attributes[index+1:])
        return Relation(attributes=attributes, elements=self.elements)

    def filter_elements(self, condition: Callable[[Element], bool]) -> "Relation":
        """
        Filters the elements in this relation set by the given predicate.
        """
        elements = list(filter(condition, self.elements))
        return Relation(attributes=self.attributes, elements=elements)


class ConstantRelation(Relation):
    attribute: Attribute
    value: Any

    def __init__(self, attribute: Attribute, value: Any):
        super().__init__(attributes=(attribute,), elements=((value,),))
        self.attribute = attribute
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)


def record_id(relation_name: str) -> Attribute:
    return Attribute(f"{relation_name}.rid")


def index(relation: Relation, index_name: str) -> tuple[Relation, Attribute]:
    rid = record_id(relation_name=index_name)
    attributes = (rid, *relation.attributes)
    elements = [(i, *element) for i, element in enumerate(sorted(relation.elements))]
    index_relation = Relation(attributes=attributes, elements=elements)
    return index_relation, rid
