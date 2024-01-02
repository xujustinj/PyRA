from typing import Union

from expression import PrefixUnaryOperator
from .relation import Relation


class Project:
    def __getitem__(
            self,
            idx: Union[int, tuple[int, ...]],
    ) -> PrefixUnaryOperator[Relation, Relation]:
        indices = list(idx) if isinstance(idx, tuple) else [idx]
        assert all(i > 0 for i in indices)
        assert len(set(indices)) == len(indices) # all indices are distinct

        name = f"\u03c0[{','.join(f'#{i}' for i in indices)}]"

        def _project(relation: Relation) -> Relation:
            call_name = f"{name} {relation}"

            A = relation.num_attributes
            for i in indices:
                assert 0 < i <= A, \
                    f"{call_name} : index #{i} out of bounds (max {A})"

            attributes = tuple(relation.attributes[i-1] for i in indices)
            elements = [
                tuple(element[i-1] for i in indices)
                for element in relation.elements
            ]
            return Relation(attributes=attributes, elements=elements)

        return PrefixUnaryOperator(_project, name=name)

project = Project()
proj = project
pi = project
