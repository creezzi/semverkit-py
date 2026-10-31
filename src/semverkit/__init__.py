"""Semantic Versioning 2.0.0: parsing, ordering, bumping and simple ranges."""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import Tuple

__all__ = ["Version", "satisfies"]

_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def _pre_key(pre: Tuple[str, ...]):
    # A version without prerelease sorts after one with; numeric ids sort before text.
    if not pre:
        return (1,)
    return (0, tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre))


@total_ordering
@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    prerelease: Tuple[str, ...] = ()
    build: Tuple[str, ...] = ()

    @classmethod
    def parse(cls, text: str) -> "Version":
        match = _SEMVER.match(text.strip().lstrip("v"))
        if not match:
            raise ValueError(f"invalid semantic version: {text!r}")
        major, minor, patch, pre, build = match.groups()
        return cls(int(major), int(minor), int(patch),
                   tuple(pre.split(".")) if pre else (), tuple(build.split(".")) if build else ())

    def _key(self):
        return (self.major, self.minor, self.patch, _pre_key(self.prerelease))

    def __eq__(self, other):
        return isinstance(other, Version) and self._key() == other._key()

    def __lt__(self, other: "Version"):
        return self._key() < other._key()

    def __hash__(self):
        return hash(self._key())

    def __str__(self):
        out = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            out += "-" + ".".join(self.prerelease)
        if self.build:
            out += "+" + ".".join(self.build)
        return out

    def bump(self, part: str) -> "Version":
        if part == "major":
            return Version(self.major + 1, 0, 0)
        if part == "minor":
            return Version(self.major, self.minor + 1, 0)
        if part == "patch":
            return Version(self.major, self.minor, self.patch + (0 if self.prerelease else 1))
        raise ValueError("part must be major, minor or patch")


def satisfies(version: str, constraint: str) -> bool:
    """Supports exact, >, >=, <, <=, ^ and ~ constraints; space means AND."""
    v = Version.parse(version)
    for clause in constraint.split():
        m = re.match(r"^(\^|~|>=|<=|>|<|=)?(.+)$", clause)
        op, target = m.group(1) or "=", Version.parse(m.group(2))
        if op == "=":
            ok = v == target
        elif op == ">":
            ok = v > target
        elif op == ">=":
            ok = v >= target
        elif op == "<":
            ok = v < target
        elif op == "<=":
            ok = v <= target
        elif op == "~":
            ok = target <= v < target.bump("minor")
        else:  # caret: allow changes that do not modify the left-most non-zero part
            if target.major > 0:
                upper = target.bump("major")
            elif target.minor > 0:
                upper = Version(0, target.minor + 1, 0)
            else:
                upper = Version(0, 0, target.patch + 1)
            ok = target <= v < upper
        if not ok:
            return False
    return True
