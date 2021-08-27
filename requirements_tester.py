#!/usr/bin/env python
import collections
import contextlib
import enum
import os
import re
import shutil
import subprocess
import sys
import typing as t
import warnings

import requirements
from requirements import requirement

PIPTOOLS_VIA_MULTILINE_PREFIX = "    #   "
PIPTOOLS_VIA_PREFIX = "    # via"

PIP_COMPILE_ERROR_REGEX = "Could not find a version that matches ([^<>=\^~]+)"
PIP_COMPILE_INCOMPATIBLE_VERSION_REGEX = ".*\(from ([^<>=\^~]+)[<>=\^~]"


# class Requirement(requirement.Requirement):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.is_primary_dependency: bool = False
#         self.requirement_for: t.List["Requirement"] = []

#     def get_children(self):
#         return [r for r in self.is_requirement_for]


# class RequirementsParser:
#     def __init__(self, src: t.Iterable[str]):
#         self._requirements_by_name: dict[str, Requirement] = {}
#         self._requirements_dependent_on: dict[str, t.Set[str]] = collections.defaultdict(set)
#         self._file_iterator = iter(src)
#         self._line: str
#         self._line_stripped: str
#         self._next()

#     def _next(self):
#         self._line = next(self._file_iterator)
#         self._line_stripped = self._line.strip()

#     def _skip_unsupported(self):
#         if (
#             self._line_stripped.startswith("-r")
#             or self._line_stripped.startswith("--requirement")
#             or self._line_stripped.startswith("-f")
#             or self._line_stripped.startswith("--find-links")
#             or self._line_stripped.startswith("-i")
#             or self._line_stripped.startswith("--index-url")
#             or self._line_stripped.startswith("--extra-index-url")
#             or self._line_stripped.startswith("--no-index")
#             or self._line_stripped.startswith("-Z")
#             or self._line_stripped.startswith("--always-unzip")
#         ):
#             self._next()
#             return True
#         return False

#     def _parse_requirement(self):
#         req: t.Optional[Requirement] = None
#         try:
#             req = Requirement.parse(self._line_stripped)
#             self._next()

#             if not self._line.startswith(PIPTOOLS_VIA_PREFIX):
#                 return

#             if self._line.rstrip() == PIPTOOLS_VIA_PREFIX:
#                 self._next()
#                 line = self._line
#             else:
#                 line = PIPTOOLS_VIA_MULTILINE_PREFIX + self._line[len(PIPTOOLS_VIA_PREFIX) + 1 :]
#             while line.startswith(PIPTOOLS_VIA_MULTILINE_PREFIX):
#                 line = line[len(PIPTOOLS_VIA_MULTILINE_PREFIX) :].strip()
#                 if line.startswith("-r"):
#                     req.is_primary_dependency = True
#                 else:
#                     self._requirements_dependent_on[req.name].add(line)
#                 self._next()
#                 line = self._line
#         finally:
#             if req:
#                 self._requirements_by_name[req.name] = req

#     def _skip_blank(self):
#         if self._line_stripped == "":
#             self._next()
#             return True
#         return False

#     def _skip_commented(self):
#         if self._line_stripped.startswith("#"):
#             self._next()
#             return True
#         return False

#     def parse(self):
#         try:
#             while True:
#                 if self._skip_commented():
#                     continue
#                 if self._skip_blank():
#                     continue
#                 if self._skip_unsupported():
#                     continue
#                 self._parse_requirement()
#         except StopIteration:
#             pass
#         for dependency_target, dependent_packages in self._requirements_dependent_on.items():
#             for pkg in dependent_packages:
#                 self._requirements_by_name[dependency_target].requirement_for.append(
#                     self._requirements_by_name[pkg]
#                 )

#         return list(self._requirements_by_name.values())


def get_problem_requirements_from_pip_compile_output(pip_compile_output: str) -> set[str]:
    problem_requirements: set[str] = set()
    for line in pip_compile_output.split("\n"):
        matches = re.match(PIP_COMPILE_ERROR_REGEX, line)
        if matches:
            print("Version conflict issue for requirement", matches.group(1))
            problem_requirements.add(matches.group(1))
            continue
        matches = re.match(PIP_COMPILE_INCOMPATIBLE_VERSION_REGEX, line)
        if matches:
            print("Version conflict issue for requirement", matches.group(1))
            problem_requirements.add(matches.group(1))
            continue

    return problem_requirements


def generate_requirements_in_file(unversioned_requirements, versioned_requirements):
    with open("requirements.test.in", "w") as f:
        for req_line in unversioned_requirements:
            f.write(req_line)
            f.write("\n")
        for req_line in versioned_requirements:
            f.write(req_line)
            f.write("\n")


def generate_requirements_txt_file(unversioned_requirements, all_requirements):
    while True:
        versioned_requirements = {
            r.line for r in all_requirements if r.name not in unversioned_requirements
        }

        generate_requirements_in_file(unversioned_requirements, versioned_requirements)

        with contextlib.suppress(FileNotFoundError):
            os.remove("requirements.dev.txt")
        with contextlib.suppress(FileNotFoundError):
            os.remove("requirements.txt")

        subprocess.run(
            ["pip-compile", "requirements.test.in", "--output-file=requirements.txt"],
            capture_output=True,
            check=True,
        )
        result = subprocess.run(
            ["pip-compile", "requirements.dev.in", "--output-file=requirements.dev.txt"],
            capture_output=True,
        )
        if result.returncode != 0:
            print("Failed to compile requirements")
            problem_requirements = get_problem_requirements_from_pip_compile_output(
                result.stderr.decode("utf-8")
            )
            if unversioned_requirements.intersection(problem_requirements) == problem_requirements:
                print(result.stderr)
                raise Exception("Cannot resolve version conflicts")
            for r in problem_requirements:
                unversioned_requirements.add(r)
            continue
        print("Requirements successfully compiled")
        return


def install_requirements_txt_file():
    subprocess.run(["pip-sync", "requirements.dev.txt"], check=True)


def run_tests():
    return subprocess.run(["pytest", "--reuse-db"]).returncode == 0

class EndNodeReached(Exception):
    def __init__(self, requirement: Requirement):
        self.requirement = requirement

class BinarySearcher:
    def __init__(self, initial_tree):
        self._initial_tree = initial_tree
        self._traversal = [[initial_tree, initial_tree[:len(initial_tree//2)]]]

    def passed(self):
        # if this is the first half, go to the second half
        if self._traversal[-1][-2][0] == self._traversal[-1][-1][0]:
            self._traversal[-1][-1] = self._traversal[-1][-2][len(self._traversal[-1]):]
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
            self._traversal.push(self._traversal[-1][-1][:len(self._traversal[-1][-1]//2)])
            return self._traversal[-1][-1]
        # if there is only a single item, see if it has children. If it has children, bisect them
        children = self._traversal[-1][-1].get_children()
        if children:
            self._traversal.push([children, children[:len(children//2)]])
            return self._traversal[-1][-1]
        raise EndNodeReached(self._traversal[-1][-1])

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



def main(args: list[str]) -> None:
    try:
        with open("requirements.txt", "r") as f:
            requirements_txt_original = f.read()

        with open("requirements.txt", "r") as f:
            reqs = RequirementsParser(f).parse()

        with open("requirements.in", "r") as f:
            reqs_in = RequirementsParser(f).parse()
            force_versioned_requirements = {req.name for req in reqs_in if req.specs}

        # leaf_requirements = [r for r in reqs if not r.requirement_for]
        unversioned_requirements = {
            r.name for r in reqs if r.name not in force_versioned_requirements
        }

        primary_dependencies = [r for r in reqs if r.is_primary_dependency]
        possible_failure_causes = set(unversioned_requirements)
        passes_with_versions = collections.defaultdict(list)
        for r in reqs:
            passes_with_versions[r.name].append(r.specs)
        # fails_when_unversioned = {r.name: False for r in reqs}

        while True:
            generate_requirements_txt_file(unversioned_requirements, reqs)
            install_requirements_txt_file()
            # subprocess.run(["pip", "install", "pip-tools"], check=True)
            if not run_tests():

                # some logic to fiddle with the requirements and try again
                # for r in possible_failure_causes:
                    # fails_when_unversioned[r] = True


                    # Unpin half the tree?
                    # for idx in range(len(primary_dependencies)//2):

    finally:
        with open("requirements.txt", "w") as f:
            f.write(requirements_txt_original)


if __name__ == "__main__":
    main(sys.argv)
