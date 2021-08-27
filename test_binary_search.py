from typing_extensions import Protocol
from searcher import BinarySearcher, EndNodeReached
import pytest

import typing as t

class ThingToBeSearched:
    def __init__(self, name: str, children: t.Optional[list["ThingToBeSearched"]] = None):
        self.name = name
        self._children = children

    def get_children(self):
        return self._children or None


# Edge cases to test
# - odd number of nodes
# - differing depths


class TestBinarySearcher:
    def test_traverses(self):
        things_to_be_searched = [
            ThingToBeSearched(
                "A",
                [
                    ThingToBeSearched("A.A"),
                    ThingToBeSearched("A.B", [ThingToBeSearched("A.B.A"), ThingToBeSearched("A.B.B")]),
                    ThingToBeSearched("A.C"),
                    ThingToBeSearched(
                        "A.D",
                        [
                            ThingToBeSearched(
                                "A.D.A",
                                [
                                    ThingToBeSearched("A.D.A.A"),
                                    ThingToBeSearched("A.D.A.B"),
                                ],
                            ),
                            ThingToBeSearched("A.D.B"),
                        ],
                    ),
                ],
            ),
            ThingToBeSearched("B"),
            ThingToBeSearched(
                "C",
                [
                    ThingToBeSearched(
                        "C.A",
                        [ThingToBeSearched("C.A.A", [ThingToBeSearched("C.A.A.A", [ThingToBeSearched("C.A.A.A.A")])])],
                    )
                ],
            ),
            ThingToBeSearched("D"),
            ThingToBeSearched("E"),
        ]

        binary_searcher = BinarySearcher(things_to_be_searched)
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A", "B"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A", "A.B", "A.C", "A.D"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A", "A.B"]
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["A.C", "A.D"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.C"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.C"
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["A.D"]
