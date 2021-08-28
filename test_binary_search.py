from searcher import BinarySearcher, EndNodeReached
import pytest

import typing as t


class ThingToBeSearched:
    def __init__(self, name: str, children: t.Optional[list["ThingToBeSearched"]] = None):
        self.name = name
        self._children = children

    def get_children(self):
        return self._children or None


class TestBinarySearcher:
    def test_single_chain(self):
        things_to_be_searched = [ThingToBeSearched("A", [ThingToBeSearched("A.A", [ThingToBeSearched("A.A.A")])])]

        binary_searcher = BinarySearcher(things_to_be_searched)
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A.A"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.A.A"
        subset = binary_searcher.passed()
        assert subset is None

    def test_single_layer_pair(self):
        things_to_be_searched = [ThingToBeSearched("A"), ThingToBeSearched("B")]

        binary_searcher = BinarySearcher(things_to_be_searched)
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A"
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["B"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "B"
        subset = binary_searcher.passed()
        assert subset is None

    def test_uneven_number(self):
        things_to_be_searched = [ThingToBeSearched("A"), ThingToBeSearched("B"), ThingToBeSearched("C")]

        binary_searcher = BinarySearcher(things_to_be_searched)
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A"
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["B", "C"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["B"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "B"
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["C"]
        subset = binary_searcher.passed()
        assert subset is None

    def test_multiple_under_single_no_initial_split_children(self):
        things_to_be_searched = [ThingToBeSearched("A", [ThingToBeSearched("A.A"), ThingToBeSearched("A.B")])]

        binary_searcher = BinarySearcher(things_to_be_searched, initial_split_children=False)
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A", "A.B"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.A.A"
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["A.B"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.B"
        subset = binary_searcher.passed()
        assert subset is None

    def test_multiple_under_single_initial_split_children(self):
        things_to_be_searched = [ThingToBeSearched("A", [ThingToBeSearched("A.A"), ThingToBeSearched("A.B")])]

        binary_searcher = BinarySearcher(things_to_be_searched, initial_split_children=True)
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.A"
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["A.B"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.B"
        subset = binary_searcher.passed()
        assert subset is None

    def test_unequal_depth(self):
        things_to_be_searched = [
            ThingToBeSearched(
                "A",
                [
                    ThingToBeSearched("A.A"),
                    ThingToBeSearched("A.B", [ThingToBeSearched("A.B.A"), ThingToBeSearched("A.B.B")]),
                ],
            )
        ]

        binary_searcher = BinarySearcher(things_to_be_searched)
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A", "A.B"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.A"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.A"
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["A.B"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.B.A", "A.B.B"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.B.A"]
        subset = binary_searcher.passed()
        assert [r.name for r in subset] == ["A.B.B"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.B.B"
        subset = binary_searcher.passed()
        assert subset is None

    def test_traverses_without_autosplit_children(self):
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
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.D.A", "A.D.B"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.D.A"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.D.A.A", "A.D.A.B"]
        subset = binary_searcher.failed()
        assert [r.name for r in subset] == ["A.D.A.A"]
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.D.A.A"
        subset = binary_searcher.passed()
        with pytest.raises(EndNodeReached) as excinfo:
            subset = binary_searcher.failed()
        excinfo.value.requirement.name = "A.D.A.B"
        subset = binary_searcher.passed()
