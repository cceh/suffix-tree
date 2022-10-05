"""A Generalized Suffix Tree."""

import collections
import itertools
from typing import Optional, Callable, Type

from . import lca_mixin, naive, ukkonen, ukkonen_gusfield
from .builder import Builder
from .node import Node, Internal
from .util import Path, UniqueEndChar, Id, Symbols

BUILDERS = [naive.Builder, ukkonen.Builder, ukkonen_gusfield.Builder]


class Tree(lca_mixin.Tree):
    """A generalized suffix tree.

    The key feature of the suffix tree is that for any leaf :math:`i`, the
    concatenation of the edgle-labels on the path from the root to leaf
    :math:`i` exactly spells out the suffix of :math:`S` that starts at point
    :math:`i`.  That is, it spells out :math:`S[i..m]`.

    Initialize and interrogate the tree:

    >>> from suffix_tree import Tree
    >>> tree = Tree({"A": "xabxac"})
    >>> tree.find("abx")
    True
    >>> tree.find("abc")
    False

    >>> tree = Tree({"A": "xabxac", "B": "awyawxacxz"})
    >>> for id_, path in tree.find_all("xac"):
    ...     print(id_, ":", str(path))
    ...
    A : x a c $
    B : x a c x z $
    >>> tree.find_all("abc")
    []

    >>> from suffix_tree import naive
    >>> tree = Tree({"A": "xabxac"}, naive.Builder)
    >>> tree.find("abx")
    True
    >>> tree.find("abc")
    False

    """

    def __init__(
        self,
        d: dict[Id, Symbols] = None,
        builder=ukkonen.Builder,
        progress: Callable[[int], None] = None,
    ):
        """Initialize and optionally build the tree.

        :param dict[Id, Symbols] d: a dictionary of ids to sequences of symbols or None
        :param builder.Builder builder: a builder
            (default = :py:class:`suffix_tree.ukkonen.Builder`)
        :param Callable progress: a progress function (default = None).  The function
            gets called at regular intervals during tree construction with one
            parameter: the current phase.
        """

        d = d or {}

        super().__init__(d)

        self.root = Internal(None, Path(tuple(), 0, 0), name="root")

        for id_, S in d.items():
            self.add(id_, S, builder, progress)

    def add(
        self,
        id_: Id,
        S: Symbols,
        builder: Type[Builder] = ukkonen.Builder,
        progress: Callable[[int], None] = None,
    ):
        """Add a sequence of symbols to the tree.

        :param object id_: an object (probably a str or int) serving as an id for the
            sequence
        :param Sequence S: a sequence of symbols
        :param builder.Builder builder: a builder
            (default = :py:class:`suffix_tree.ukkonen.Builder`)
        :param Callable progress: a progress function (default = None).  The function
            gets called at regular intervals during tree construction with one
            parameter: the current phase.


        >>> from suffix_tree import Tree
        >>> tree = Tree()
        >>> tree.add("A", "xabxac")
        >>> tree.add("B", "awyawxawxz")
        >>> tree.find("abx")
        True
        >>> tree.find("awx")
        True
        >>> tree.find("abc")
        False
        """

        # input is any iterable, make an immutable copy with a unique
        # character at the end
        path = Path.from_iterable(itertools.chain(S, [UniqueEndChar(id_)]))

        self.builder = builder(self, id_, path)
        self.builder.set_progress_function(progress)
        self.builder.build()

    def find_path(self, path: Path) -> tuple[Node, int, Optional[Node]]:
        """Find a path in the tree.

        See: :py:func:`suffix_tree.node.Internal.find_path`

        """
        return self.root.find_path(path)

    def find(self, S: Symbols) -> bool:
        """Find a sequence in the tree.

        :param Sequence S: a sequence of symbols
        :return: True if the sequence was found in the tree.

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac"})
        >>> tree.find("abx")
        True
        >>> tree.find("abc")
        False
        """

        path = Path.from_iterable(S)
        dummy_node, matched_len, dummy_child = self.find_path(path)
        return matched_len == len(path)

    def find_all(self, S: Symbols) -> list[tuple[Id, Path]]:
        """Find all occurences of a sequence in a tree.

        :param Sequence S: a sequence of symbols
        :return: a list of positions

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac"})
        >>> for id_, path in tree.find_all("ab"):
        ...     print(id_, ":", str(path))
        ...
        A : a b x a c $
        >>> tree.find_all("abc")
        []
        """

        path = Path.from_iterable(S)
        node, matched_len, child = self.find_path(path)
        if matched_len < len(path):
            return []
        return (child or node).get_positions()

    def find_id(self, id_: Id, S: Symbols) -> bool:
        r"""Find a sequence in the tree.

        :param object id_: the id of a sequence in the tree
        :param Sequence S: a given sequence of symbols
        :return: True if the given sequence was found in the tree in the sequence
            labeled with id\_.

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
        >>> tree.find_id("A", "abx")
        True
        >>> tree.find_id("B", "awx")
        True
        >>> tree.find_id("B", "abx")
        False
        """

        for i, dummy_p in self.find_all(S):
            if i == id_:
                return True
        return False

    def pre_order(self, f) -> None:
        """Walk the tree visiting each node before its children.

        :param Callable f: the visitor function
        """
        self.root.pre_order(f)

    def post_order(self, f) -> None:
        """Walk the tree visiting each node after its children.

        :param Callable f: the visitor function
        """
        self.root.post_order(f)

    def common_substrings(self) -> list[tuple[int, int, Path]]:
        """Get a list of common substrings.

        **Definition** Let :math:`K` be the number of sequences in the tree.  For each
        :math:`k` between 2 and :math:`K`, we define :math:`l(k)` to be the length of
        the *longest substring common to at least* :math:`k` *of the strings.*
        --- [Gusfield1997]_ §7.6, page 127ff

        :return: a list of tuples containing :math:`k`, :math:`l(k)`, and the Path.

        >>> from suffix_tree import Tree
        >>> tree = Tree(
        ...     {
        ...         "A": "sandollar",
        ...         "B": "sandlot",
        ...         "C": "handler",
        ...         "D": "grand",
        ...         "E": "pantry",
        ...     }
        ... )
        >>> for k, lk, path in tree.common_substrings():
        ...     print(k, lk, path)
        ...
        2 4 s a n d
        3 3 a n d
        4 3 a n d
        5 2 a n
        """

        self.root.compute_C()

        V: dict[int, tuple[int, Id, Path]] = collections.defaultdict(
            lambda: (0, "no_id", None)  # type: ignore
        )  # C => (string_depth, id, path)

        self.root.common_substrings(V)  #  pre_order(f)

        l: list[tuple[int, int, Path]] = []
        max_len = 0
        max_path = None
        for k in range(max(V.keys()), 1, -1):
            length = V[k][0]
            if length > max_len:
                max_len = length
                max_path = V[k][2]
            l.append((k, max_len, max_path))  # type: ignore
        return sorted(l)

    def maximal_repeats(self) -> list[tuple[int, Path]]:
        r"""Get a list of the maximal repeats in the tree.

        **Definition** A *maximal pair* in a string :math:`S` is a pair of identical
        substrings :math:`\alpha` and :math:`\beta` in :math:`S` such that the character
        to immediate left (right) of :math:`\alpha` is different from the character to
        the immediate left (right) of :math:`\beta`.  That is, extending :math:`\alpha`
        and :math:`\beta` in either direction would destroy the equality of the two
        strings.  A *maximal repeat* :math:`\alpha` is a *substring* of :math:`S` that
        occurs in a maximal pair in :math:`S`. --- [Gusfield1997]_ §7.12, page 143ff.

        :return: a list of tuples of :math:`C` and path, where :math:`C` is the number
            of distinct sequences in the tree that contain the maximal repeat.

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
        >>> for C, path in sorted(tree.maximal_repeats()):
        ...     print(C, path)
        ...
        1 a w
        1 a w x
        2 a
        2 x
        2 x a

        """
        self.root.compute_C()
        self.root.compute_left_diverse()

        l: list[tuple[int, Path]] = []
        for child in self.root.children.values():
            child.maximal_repeats(l)
        return l

    def to_dot(self) -> str:
        """Output the tree in GraphViz .dot format.

        :return: the tree in GraphViz dot format.
        """
        dot = []
        dot.append("strict digraph G {\n")
        self.root.to_dot(dot)
        dot.append("}\n")
        return "".join(dot)
