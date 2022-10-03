"""Utilities for suffix tree."""

import collections
import logging
import subprocess
import sys
from typing import Optional, cast, overload

# python 3.10+
# Id: TypeAlias = object
# Symbol: TypeAlias = collections.abc.Hashable
# Symbols: TypeAlias = collections.abc.Sequence[Symbol]

Id = object
Symbol = collections.abc.Hashable
Symbols = collections.abc.Sequence[Symbol]

DEBUG = False
""" Print lots of debug information. """
DEBUG_DOT = False
""" Write out dot files of the tree at the end of each phase. """
DEBUG_LABELS = False
""" Include more (potentially confusing) information in node labels. """


class UniqueEndChar:  # pylint: disable=too-few-public-methods
    """A singleton object to signal end of sequence."""

    def __init__(self, id_):
        self.id: Id = id_

    def __str__(self):
        return "$"


min_debug_depth = -1
""" How deep we were in the stack when emitting the first debug message.

Used to print the interesting part of the stack.
"""


def debug(msg: str, *args, **kwargs) -> None:
    """Print a debug message to stderr."""

    if __debug__ and DEBUG:
        global min_debug_depth  # pylint: disable=global-statement

        frame = sys._getframe(1)  # pylint: disable=protected-access
        function_name = frame.f_code.co_name
        depth = 0
        while frame.f_back:
            frame = frame.f_back
            depth += 1
        if min_debug_depth == -1:
            min_debug_depth = depth
        depth -= min_debug_depth
        msg = f"{'  ' * depth}{function_name}: {msg}"
        logging.debug(msg, *args, **kwargs)


def debug_dot(tree, filename: str) -> None:
    """Write a dot and png file of the tree."""

    if __debug__ and DEBUG_DOT:
        dot = tree.to_dot()
        debug("writing dot: %s", filename)
        with open(f"{filename}.dot", "w") as tmp:
            tmp.write(dot)
        subprocess.check_output(
            f"dot -Tpng {filename}.dot > {filename}.png", shell=True
        )


def is_debug() -> bool:
    """Return True if debugging is on."""

    return __debug__ and DEBUG


class Path:
    """A path in a suffix tree.

    Paths come in two flavors: closed and open-ended.  A closed path has a fixed end.
    In an open-ended path the end is implicitly equivalent to the current phase. When
    the current phase of the builder increments, the end of all open-ended paths gets
    incremented too.  This is implemented by the property :code:`end` pointing to a
    mutable integer (an integer stored in an array, so we can replace the integer in the
    array).
    """

    __slots__ = "S", "start", "_end"

    @overload
    def __init__(self, S: Symbols, start: int, end: int):
        ... # pragma: no cover

    @overload
    def __init__(self, S: "Path", start: int, end: Optional[int]):
        ... # pragma: no cover

    def __init__(self, S, start, end):
        """Initialize a path from a sequence of symbols or another path.

        If end is None it is copied from the other path.
        """

        if isinstance(S, Path):
            self.S: Symbols = S.S
            self.start: int = start
            self._end: list[int] = [end] if end is not None else S._end
            """_end emulates a mutable integer.
            See: Gusfield, 6.1.5 Single Phase Algorithm, Pg. 106, step 1 and
            6.1.6 Creating the true suffix tree."""
        else:
            self.S = S
            self.start = start
            self._end = [end]

        assert (
            0 <= start <= self.end <= len(self.S)
        ), f"Path: 0 <= {start} <= {self.end} <= {len(self.S)}"

    @property
    def end(self) -> int:
        """Return the end of the path.

        This is a calculated property because sometimes the end is 'infinity', which
        means that the end is assumed to be the end of the current phase.

        """
        return self._end[0]

    @end.setter
    def end(self, value: int) -> None:
        """Set a new array used only by this path."""
        self._end = [value]

    def set_open_end(self, value: int) -> None:
        """Set the open end marker.

        This puts the value in an array used by many paths.  We can replace the value in
        the array.
        """
        self._end[0] = value

    @property
    def k(self) -> int:
        """Return the start of the path in Ukkonen's preferred notation."""

        return self.start

    @property
    def p(self) -> int:
        """Return the end of the path in Ukkonen's preferred notation."""

        return self._end[0] - 1

    @property
    def i(self) -> int:
        """Another end of the path in Ukkonen's preferred notation."""

        return self._end[0] - 1

    @classmethod
    def from_iterable(cls, iterable: collections.abc.Iterable[Symbol]) -> "Path":
        """Build a path from an iterable."""

        if isinstance(iterable, collections.abc.Sequence):
            return Path(
                cast(collections.abc.Sequence[Symbol], iterable), 0, len(iterable)
            )

        # make it a collection because we need __len__
        tup = tuple(iterable)
        return Path(tup, 0, len(tup))

    def __str__(self) -> str:
        return " ".join(map(str, self.S[self.start : self.end]))

    def __len__(self) -> int:
        return self.end - self.start

    def __lt__(self, other) -> bool:
        """Return True if self less than other.

        Convenience function that allows to sort paths if the symbols are sortable.  Not
        used in tree construction.
        """
        # raise NotImplemented
        return self.S[self.start : self.end] < other.S[other.start : other.end]

    def __getitem__(self, i: int) -> Symbol:
        """Return the symol at position i.

        Note: this should implement slices but we don't need them.
        Also we don't need negative indices.
        """
        return self.S[self.start + i]

    def compare(self, path: "Path", offset: int = 0) -> int:
        """Compare a path against another, return the matched length."""
        length = min(len(self), len(path)) - offset
        offset1 = self.start + offset
        offset2 = path.start + offset
        i = 0

        while i < length:
            if self.S[offset1 + i] != path.S[offset2 + i]:
                break
            i += 1
        if __debug__ and DEBUG:
            debug(
                "Comparing %s == %s at offsets %d => common len: %d",
                str(self),
                str(path),
                offset,
                i,
            )
        return i

    def ukko_str(self) -> str:
        """Debug path in Ukkonen's notation."""
        return f'k={self.k} p={self.p} k..p="{str(self)}"'
