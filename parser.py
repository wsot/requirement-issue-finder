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


class Requirement(requirement.Requirement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_primary_dependency: bool = False
        self.requirement_for: t.List["Requirement"] = []

    def get_children(self):
        return [r for r in self.is_requirement_for]


class RequirementsParser:
    def __init__(self, src: t.Iterable[str]):
        self._requirements_by_name: dict[str, Requirement] = {}
        self._requirements_dependent_on: dict[str, t.Set[str]] = collections.defaultdict(set)
        self._file_iterator = iter(src)
        self._line: str
        self._line_stripped: str
        self._next()

    def _next(self):
        self._line = next(self._file_iterator)
        self._line_stripped = self._line.strip()

    def _skip_unsupported(self):
        if (
            self._line_stripped.startswith("-r")
            or self._line_stripped.startswith("--requirement")
            or self._line_stripped.startswith("-f")
            or self._line_stripped.startswith("--find-links")
            or self._line_stripped.startswith("-i")
            or self._line_stripped.startswith("--index-url")
            or self._line_stripped.startswith("--extra-index-url")
            or self._line_stripped.startswith("--no-index")
            or self._line_stripped.startswith("-Z")
            or self._line_stripped.startswith("--always-unzip")
        ):
            self._next()
            return True
        return False

    def _parse_requirement(self):
        req: t.Optional[Requirement] = None
        try:
            req = Requirement.parse(self._line_stripped)
            self._next()

            if not self._line.startswith(PIPTOOLS_VIA_PREFIX):
                return

            if self._line.rstrip() == PIPTOOLS_VIA_PREFIX:
                self._next()
                line = self._line
            else:
                line = PIPTOOLS_VIA_MULTILINE_PREFIX + self._line[len(PIPTOOLS_VIA_PREFIX) + 1 :]
            while line.startswith(PIPTOOLS_VIA_MULTILINE_PREFIX):
                line = line[len(PIPTOOLS_VIA_MULTILINE_PREFIX) :].strip()
                if line.startswith("-r"):
                    req.is_primary_dependency = True
                else:
                    self._requirements_dependent_on[req.name].add(line)
                self._next()
                line = self._line
        finally:
            if req:
                self._requirements_by_name[req.name] = req

    def _skip_blank(self):
        if self._line_stripped == "":
            self._next()
            return True
        return False

    def _skip_commented(self):
        if self._line_stripped.startswith("#"):
            self._next()
            return True
        return False

    def parse(self):
        try:
            while True:
                if self._skip_commented():
                    continue
                if self._skip_blank():
                    continue
                if self._skip_unsupported():
                    continue
                self._parse_requirement()
        except StopIteration:
            pass
        for dependency_target, dependent_packages in self._requirements_dependent_on.items():
            for pkg in dependent_packages:
                self._requirements_by_name[dependency_target].requirement_for.append(self._requirements_by_name[pkg])

        return list(self._requirements_by_name.values())
