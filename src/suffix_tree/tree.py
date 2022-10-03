"""A Generalized Suffix Tree.

See: README.rst.

"""

import collections
import itertools
from typing import Optional, Callable, Type

from . import lca_mixin, naive, ukkonen, ukkonen_gusfield
from .builder import Builder
from .node import Node, Internal
from .util import Path, UniqueEndChar, is_debug, Id, Symbols

BUILDERS = [naive.Builder, ukkonen.Builder, ukkonen_gusfield.Builder]


class Tree(lca_mixin.Tree):
    """A suffix tree.

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
        """Initialize and build the tree from a dict of iterables.

        :param dict d: a dictionary of Id: Items
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
        """Add items to the tree.

        :param string id_: an id
        :param iterable S: an iterable of hashables
        :param Builder builder: a builder (default = Ukkonen)
        :param Callable progress: a progress function (default = None)

        The progress function gets called at regular intervals during tree construction.
        The parameter is the current phase.

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

        Returns the deepest node on the path, the matched length of the path,
        and also the next deeper node if the matched length is longer than the
        string-depth of the deepest node on the path.

        """
        return self.root.find_path(path)

    def find(self, items: Symbols) -> bool:
        """Return True if the string is found.

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac"})
        >>> tree.find("abx")
        True
        >>> tree.find("abc")
        False
        """

        path = Path.from_iterable(items)
        dummy_node, matched_len, dummy_child = self.find_path(path)
        return matched_len == len(path)

    def find_all(self, items: Symbols):
        """Return all indices of path in tree.

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac"})
        >>> for id_, path in tree.find_all("ab"):
        ...     print(id_, ":", str(path))
        ...
        A : a b x a c $
        >>> tree.find_all("abc")
        []
        """

        path = Path.from_iterable(items)
        node, matched_len, child = self.find_path(path)
        if matched_len < len(path):
            return []
        return (child or node).get_positions()

    def find_id(self, id_: Id, items: Symbols) -> bool:
        """Return True if a string is found with the corresponding id.

        :param string id_: an id
        :param iterable S: an iterable of hashables

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
        >>> tree.find_id("A", "abx")
        True
        >>> tree.find_id("B", "awx")
        True
        >>> tree.find_id("B", "abx")
        False
        """

        for i, dummy_p in self.find_all(items):
            if i == id_:
                return True
        return False

    def pre_order(self, f) -> None:
        """Walk the tree in visiting each node before its children."""
        self.root.pre_order(f)

    def post_order(self, f) -> None:
        """Walk the tree in visiting each node after its children."""
        self.root.post_order(f)

    def common_substrings(self) -> list[tuple[int, int, Path]]:
        """Get a list of common substrings.

        **Definition** For each :math:`k` between 2 and :math:`K`, we define
        :math:`l(k)` to be the length of the *longest substring common to at
        least* :math:`k` *of the strings.*

        Returns a table of :math:`K - 1` entries, where entry :math:`k` gives
        :math:`l(k)`.

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
        >>> for k, length, path in tree.common_substrings():
        ...     print(k, length, path)
        ...
        2 4 s a n d
        3 3 a n d
        4 3 a n d
        5 2 a n

        [Gusfield1997]_ §7.6, 127ff
        """

        self.root.compute_C()

        V: dict[int, tuple[int, Id, Path]] = collections.defaultdict(
            lambda: (0, "no_id", None)  # type: ignore
        )  # C => (string_depth, id, path)

        def f(node):
            """Collect common substrings into V."""
            k = node.C  # no. of distinct strings in the subtree
            sd = node.string_depth()
            if sd > V[k][0]:
                for id_, path in node.get_positions():  # pragma: no branch
                    # select an arbitrary one (the first)
                    # change the path to stop at this node
                    V[k] = (sd, id_, Path(path, path.start, path.start + sd))
                    break

        self.root.pre_order(f)

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
        """Get a list of the maximal repeats in the tree.

        N.B.  The repeats must be in different input strings.

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

        See [Gusfield1997]_ §7.12.1, 144ff.

        """
        self.root.compute_C()
        self.root.compute_left_diverse()

        a: list[tuple[int, Path]] = []
        for child in self.root.children.values():
            child.maximal_repeats(a)
        return a

    def to_dot(self) -> str:
        """Output the tree in GraphViz .dot format."""
        dot = []
        dot.append("strict digraph G {\n")
        self.root.to_dot(dot)
        dot.append("}\n")
        return "".join(dot)
