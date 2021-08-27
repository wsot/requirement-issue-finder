from reqparser import Requirement
import typing as t


class EndNodeReached(Exception):
    def __init__(self, requirement: Requirement):
        self.requirement = requirement


class BinarySearcher:
    def __init__(self, initial_tree):
        self._initial_tree = initial_tree
        self._traversal = [[initial_tree]]
        # self._traversal = [[initial_tree, initial_tree[: len(initial_tree // 2)]]]

    def passed(self):
        # if this is the first half, go to the second half
        if self._traversal[-1][-2][0] == self._traversal[-1][-1][0]:
            self._traversal[-1][-1] = self._traversal[-1][-2][len(self._traversal[-1]) :]
            return self._traversal[-1][-1]

        # otherwise this must already be the second half of the current subset
        # possibilities are:
        #  - there are parents within the current traversal subset
        #  - there are no more parents within the current traversal subset, but there are parent subsets
        #  - there are no more parents within the current traversal subset, and there are no more parent subsets - we're finished

        # go up a level in the current subset and try again
        self._traversal[-1].pop()

        # if there isn't another level inside the current subset, move to the parent subset then try again
        if not len(self._traversal[-1]) > 1:
            self._traversal.pop()
            if not len(self._traversal) > 1:
                # Ok, that's the end of the pile
                return
            self._traversal.pop()
        return self.passed()

    def failed(self):
        # if there is more than a single item, then bisect it
        if len(self._traversal[-1][-1]) > 1:
            self._traversal[-1].append(self._traversal[-1][-1][: len(self._traversal[-1][-1]) // 2])
            return self._traversal[-1][-1]
        # if there is only a single item, see if it has children. If it has children, bisect them
        children = self._traversal[-1][-1][0].get_children()
        if children:
        #     self._traversal.append([children, children[: len(children) // 2]])
            self._traversal.append([children])
            return self._traversal[-1][-1]
        raise EndNodeReached(self._traversal[-1][-1][0])

    # if first item of current bottom level == first item of parent level, then you're doing the first half

    # start with half of the top level of the unpinned. If that passes, get the next half of that level of the tree.
    # if it fails, test with half of that top level.
    # If we're down to one in the top level, go to half the children of that. IF it passes, go to the next half. If it fails, split the current half.
    # if the current half is 'one', then see if it has children. If it has children, test pinning them.

    # test with none pinned; if fails, pin half and all descendents of that half; if p

    # if something fails when unpinned, but passes when pinned, that thing being pinned is contributing
    # then try to isolate the smallest group that can be pinned

    # start with nothing pinned

    # failure can be because top level version changes, or because children change - need to be able to differentiate
    # if fully pinned passes, unpin half of tree all the way down. If that passes, unpin half that tree all the way down. If it fails, pin the other half.
