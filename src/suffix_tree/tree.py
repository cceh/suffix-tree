"""A Generalized Suffix Tree."""

import collections
import itertools
from typing import Dict, List, Optional, Tuple, Union

from . import lca_mixin
from .builder import Builder
from .builder_factory import builder_factory
from .node import Internal, Node
from .util import Id, Path, Symbols, UniqueEndChar

# builder_type: TypeAlias = Union[Builder, type, str, None]
builder_type = Union[Builder, type, str, None]


class Tree(lca_mixin.Tree):
    """A generalized suffix tree.

    The key feature of the suffix tree is that for any leaf `i`, the
    concatenation of the edgle-labels on the path from the root to leaf
    `i` exactly spells out the suffix of `S` that starts at point
    `i`.  That is, it spells out `S[i..m]`.

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
    >>> tree = Tree({"A": "xabxac"}, builder=naive.Builder)
    >>> tree.find("abx")
    True
    >>> tree.find("abc")
    False

    """

    def __init__(
        self,
        data: Optional[Dict[Id, Symbols]] = None,
        *,
        builder: builder_type = None,
    ):
        """Initialize and optionally build the tree.

        :param Dict[Id, Symbols] data: a dictionary of ids to sequences of symbols
            or None
        :param builder.Builder builder: a builder
            (default = :py:class:`suffix_tree.ukkonen.Builder`)
        :param Callable progress: a progress function (default = None).  The function
            gets called at regular intervals during tree construction with one
            parameter: the current phase.
        """

        d = data or {}

        super().__init__(d)

        self.root = Internal(None, tuple(), 0, 0)
        self.root.name = "root"

        for id_, S in d.items():
            self.add(id_, S, builder=builder)

    def add(
        self,
        id_: Id,
        S: Symbols,
        *,
        builder: builder_type = None,
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

        if builder is None:
            builder = builder_factory()
        if isinstance(builder, str):
            builder = builder_factory(builder)
        if isinstance(builder, type):
            builder = builder()
        assert isinstance(builder, Builder)
        builder.build(self.root, id_, itertools.chain(S, [UniqueEndChar(id_)]))

    def find_path(self, path: Path) -> Tuple[Node, int, Optional[Node]]:
        """Find a path in the tree.

        See: :py:func:`suffix_tree.node.Internal.find_path`

        """
        return self.root.find_path(path.S, path.start, path.end)

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

        path = Path(S)
        dummy_node, matched_len, dummy_child = self.find_path(path)
        return matched_len == len(path)

    def find_all(self, S: Symbols) -> List[Tuple[Id, Path]]:
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

        path = Path(S)
        node, matched_len, child = self.find_path(path)
        if matched_len < len(path):
            return []
        if child is not None:
            return child.get_positions()
        return node.get_positions()

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

    def common_substrings(self) -> List[Tuple[int, int, Path]]:
        """Compute a common substring table.

        Suppose we have `K` strings.

        **Definition** For each `k` between 2 and `K`, we define `l(k)` to be the length
        of the *longest substring common to at least* `k` *of the strings.*

        We want to compute a table of `K - 1` entries, where entry `k` gives `l(k)` and
        also points to one of the common substrings of that length.
        --- [Gusfield1997]_ §7.6, page 127ff

        :return: a list of `K - 1` tuples containing `k`, `l(k)`, and one of the common
                 substrings of that length, which may be None.

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

        V: Dict[int, Tuple[int, Id, Path]] = collections.defaultdict(
            lambda: (0, "no_id", None)  # type: ignore
        )  # C => (depth, id, path)

        self.root.common_substrings(V)  #  pre_order(f)

        l: List[Tuple[int, int, Path]] = []
        max_len = 0
        max_path = None
        for k in range(max(V.keys()), 1, -1):
            length = V[k][0]
            if length > max_len:
                max_len = length
                max_path = V[k][2]
            l.append((k, max_len, max_path))  # type: ignore
        return sorted(l)

    def maximal_repeats(self) -> List[Tuple[int, Path]]:
        r"""Get a list of the maximal repeats in the tree.

        **Definition** A *maximal pair* in a string `S` is a pair of identical
        substrings `\alpha` and `\beta` in `S` such that the character
        to immediate left (right) of `\alpha` is different from the character to
        the immediate left (right) of `\beta`.  That is, extending `\alpha`
        and `\beta` in either direction would destroy the equality of the two
        strings.  A *maximal repeat* `\alpha` is a *substring* of `S` that
        occurs in a maximal pair in `S`. --- [Gusfield1997]_ §7.12, page 143ff.

        :return: a list of tuples of `C` and path, where `C` is the number
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

        l: List[Tuple[int, Path]] = []
        for child in self.root.children.values():
            child.maximal_repeats(l)
        return l
