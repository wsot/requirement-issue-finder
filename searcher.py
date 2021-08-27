from reqparser import Requirement
import typing as t


class EndNodeReached(Exception):
    def __init__(self, requirement: Requirement):
        self.requirement = requirement


class BinarySearcher:
    def __init__(self, initial_tree, initial_split_children=False):
        self._initial_tree = initial_tree
        self._traversal = [[initial_tree]]
        self._initial_split_children = initial_split_children

    def passed(self):
        # if there is no parent list, we're done
        if not len(self._traversal) > 0:
            return None

            # if the parent list is only one item, skip past it as it has already been traversed downward
        if not len(self._traversal[-1]) > 1:
            self._traversal.pop()
            return self.passed()

        # if this is the first half, go to the second half
        if self._traversal[-1][-2][0] == self._traversal[-1][-1][0]:
            self._traversal[-1][-1] = self._traversal[-1][-2][len(self._traversal[-1][-2]) // 2 :]
            return self._traversal[-1][-1]

        # otherwise this must already be the second half of the current subset
        # possibilities are:
        #  - there are parents within the current traversal subset
        #  - there are no more parents within the current traversal subset, but there are parent subsets
        #  - there are no more parents within the current traversal subset, and there are no more parent subsets - we're finished

        # go up a level in the current subset and try again
        self._traversal[-1].pop()
        return self.passed()

    def failed(self):
        # if there is more than a single item, then bisect it
        if len(self._traversal[-1][-1]) > 1:
            self._traversal[-1].append(self._traversal[-1][-1][: len(self._traversal[-1][-1]) // 2])
            return self._traversal[-1][-1]
        # if there is only a single item, see if it has children. If it has children, bisect them
        children = self._traversal[-1][-1][0].get_children()
        if children:
            if self._initial_split_children:
                # Assume that the parent is equivalent to the full list of children, so split the children immediately
                self._traversal.append([children, children[: len(children) // 2]])
            else:
                # Assume that the parent and full list of children are distinct,
                #  so each should be independently represented when traversing the tree
                self._traversal.append([children])
            return self._traversal[-1][-1]
        raise EndNodeReached(self._traversal[-1][-1][0])
