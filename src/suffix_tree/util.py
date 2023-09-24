"""Utilities for suffix tree."""

import collections
import logging
import sys
from typing import Sequence, Iterable

# python 3.10+
# Id: TypeAlias = object
# Symbol: TypeAlias = collections.abc.Hashable
# Symbols: TypeAlias = collections.abc.Sequence[Symbol]

Id = object
Symbol = collections.abc.Hashable
Symbols = Sequence[Symbol]
IterSymbols = Iterable[Symbol]

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


def is_debug() -> bool:
    """Return True if debugging is on."""

    return __debug__ and DEBUG


def ukko_str(S: Symbols, start: int, end: int) -> str:
    """Debug path in Ukkonen's preferred notation."""
    return f'k={start} p={end-1} k..p="{str(S[start:end])}"'


class Path:
    """A path in a suffix tree."""

    __slots__ = "S", "start", "end"

    def __init__(self, S, start=0, end=None):
        """Initialize a path from a sequence of symbols.

        If end is None it is set to the length of the sequence.
        """
        self.S = S
        self.start = start
        self.end = end or len(S)

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
