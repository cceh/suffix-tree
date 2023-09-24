"""Node classes for a Generalized Suffix Tree."""

from typing import Optional, Tuple, List, Set, Dict

from .util import Path, Id, Symbol, Symbols, debug
from . import lca_mixin, util

EMPTY_STR = ""


class Node(lca_mixin.Node):
    """The abstract base class for internal and leaf nodes."""

    __slots__ = (
        "parent",
        "S",
        "start",
        "end",
        "depth",
        "name",
    )

    def __init__(
        self, parent: Optional["Internal"], S: Symbols, start: int, end: int
    ):  # pragma: no cover
        super().__init__()

        self.parent = parent
        """The parent of this node.  Used by Ukkonen and LCA."""

        self.S = S
        """The sequence of symbols. In a generalized tree the first sequence that
        created this node. S[start:end] is the path-label of this node."""
        self.start = start
        """The start position in S of the path-label that goes into this node."""
        self.end = end
        """The end position in S of the path-label that goes into this node."""
        self.depth = end - start

        self.name: str = EMPTY_STR
        """A name that can be given to the node.  The name is used only for debugging.
        It is reported in the debug dot graph.
        """

    def __str__(self) -> str:
        """Return a string representaion of this node for debugging."""
        raise NotImplementedError()

    def __getitem__(self, i: int) -> Symbol:
        """Return the symol at position i.

        Note: this should implement slices but we don't need them.
        Also we don't need negative indices.
        """
        return self.S[self.start + i]

    def compute_C(self) -> Set[Id]:
        """Calculate the `C(v)` number for this node and all its children."""
        raise NotImplementedError()

    def compute_left_diverse(self):
        """Calculate the left-diversity of this node and all its children."""
        raise NotImplementedError()

    def pre_order(self, f) -> None:
        """Walk the tree visiting each node before its children.

        :param Callable f: the visitor function
        """
        raise NotImplementedError()

    def post_order(self, f) -> None:
        """Walk the tree visiting each node after its children.

        :param Callable f: the visitor function
        """
        raise NotImplementedError()

    def add_position(self, l: List[Tuple[Id, Path]]) -> None:
        """If this node is a Leaf, then add the path to the list."""
        raise NotImplementedError()

    def get_positions(self) -> List[Tuple[Id, Path]]:
        """Get all paths that traverse this node."""
        paths: List[Tuple[Id, Path]] = []
        self.pre_order(lambda self_: self_.add_position(paths))
        return paths

    def common_substrings(self, _V: Dict[int, Tuple[int, Id, Path]]):
        """Common substrings recursive function."""
        return

    def maximal_repeats(self, a: list):
        """Maximal repeats recursive function."""
        raise NotImplementedError()

    def _to_dot(self, a: List[str]) -> None:
        """Translate the node into Graphviz .dot format."""
        raise NotImplementedError()

    def to_dot(self) -> str:
        """Output the tree in GraphViz .dot format.

        :return: the tree in GraphViz dot format.
        """
        dot = []
        dot.append("strict digraph G {\n")
        self._to_dot(dot)
        dot.append("}\n")
        return "".join(dot)

    def debug_dot(self, filename: str) -> None:
        """Write a dot file of the tree."""

        if __debug__ and util.DEBUG_DOT:
            debug("writing dot: %s", filename)
            with open(filename, "w") as tmp:
                tmp.write(self.to_dot())


class Internal(lca_mixin.Internal, Node):
    """An internal node.

    Internal nodes are created for the root and auxiliary node and when splitting edges.
    Internal nodes have at least 2 children and a fixed end.
    """

    __slots__ = (
        "suffix_link",
        "children",
        "is_left_diverse",
        "C",
    )

    def __init__(
        self, parent: Optional["Internal"], S: Symbols, start: int, end: int
    ):  # pylint: disable=super-init-not-called
        # save the super call by inlining
        # super().__init__(parent, S, start, end)
        self.parent = parent
        self.S = S
        self.start = start
        self.end = end
        self.name: str = EMPTY_STR
        self.lca_id = 0
        self.I = 0
        self.A = 0

        self.suffix_link: Optional[Internal] = None
        r"""Used by the McCreight and Ukkonen algorithms to speed up the construction of
        the tree.

        "**Corollary 6.1.2** In any implicit suffix tree `\mathcal{T}_i', if
        internal node `v` has path-label `x\alpha`, then *there is* a node
        `s(v)` of `\mathcal{T}_i` with path-label `\alpha`."
        --- [Gusfield1997]_ page 98
        """

        self.depth = end - start
        """Cache the depth value."""

        self.children: dict[Symbol, Node] = {}
        """ A dictionary of item => node """

        self.is_left_diverse: Optional[bool] = None
        r"""**Definition** A node `v` of `\mathcal{T}` is called *left
        diverse* if at least two leaves in `v`'s subtree have different left
        characters.  By definition a leaf cannot be left diverse.

        For each position `i` in string `S`, character `S(i-1)` is
        called the *left character* of `i`. The *left character of a leaf* of
        `\mathcal{T}` is the left character of the suffix position represented by
        that leaf. --- [Gusfield1997]_ §7.12.1, page 144ff

        N.B. This suffix tree operates on any python hashable object, not just
        characters, so left characters usually are objects.
        """

        self.C: int = -1
        r"""**Definition** For any internal node `v` of `\mathcal{T}`,
        define `C(v)` to be the number of *distinct* string identifiers that
        appear at the leaves in the subtree of `v`. --- [Gusfield1997]_ §7.6, page
        127ff
        """

    def __str__(self) -> str:
        return (
            "Internal '"
            + (self.name or " ".join(map(str, self.S[self.start : self.end])))
            + "'"
        ) + super().__str__()

    def add_position(self, l: List[Tuple[Id, Path]]) -> None:
        return

    def pre_order(self, f) -> None:
        f(self)
        for node in self.children.values():
            node.pre_order(f)

    def post_order(self, f) -> None:
        for node in self.children.values():
            node.post_order(f)
        f(self)

    def find_path(
        self, S: Symbols, start: int, end: int
    ) -> Tuple["Node", int, Optional["Node"]]:
        """Find a path starting from this node.

        The path is absolute.

        Returns the deepest node on the path, the matched length of the path,
        and also the next deeper node if the matched length is longer than the
        string-depth of the deepest node on the path.
        """
        node: Node = self
        matched_len = self.depth
        max_len = end - start

        while matched_len < max_len:
            # find the edge to follow
            assert isinstance(node, Internal)
            child = node.children.get(S[start + matched_len])  # type: ignore
            if child is not None:
                # follow the edge
                stop = min(child.depth, max_len)
                while matched_len < stop:
                    if child.S[child.start + matched_len] != S[start + matched_len]:
                        break
                    matched_len += 1
                if matched_len < child.depth:
                    # the path ends between node and child
                    return node, matched_len, child
                # we reached another node, loop
                node = child
            else:
                # no edge to follow
                return node, matched_len, None
        # path exhausted
        return node, matched_len, None

    def split_edge(self, new_len: int, child: Node) -> "Internal":
        """Split the edge from self to child.

        Split *self --> child* into *self --> new_node --> child* and return new_node.

        :param int new_len: the length of the path into the new node
        :param Node child: indicates the edge to split
        :return: the new node
        """
        assert (
            self.depth < new_len < child.depth
        ), f"split length {self.depth} => {new_len} => {child.depth}"

        # note: start is the start of the path-label not of the edge-label
        # note: self.end != child.start if self.S != child.S
        new_edge_end = child.start + new_len
        # it is always safe to shorten a path
        new_node = Internal(self, child.S, child.start, new_edge_end)

        self.children[
            child.S[child.start + self.depth]
        ] = new_node  # substitute new node
        new_node.children[child.S[new_edge_end]] = child
        child.parent = new_node

        if __debug__ and util.DEBUG:
            debug("Splitting Edge %s----%s", str(self), str(child))
            debug(
                "Into           %s----%s----%s",
                str(self),
                str(new_node),
                str(child),
            )

        return new_node

    def compute_C(self) -> Set[Id]:
        id_set: Set[Id] = set()
        for node in self.children.values():
            id_set.update(node.compute_C())
        self.C = len(id_set)
        return id_set

    def compute_left_diverse(self) -> Optional[Set]:
        left_characters = set()
        self.is_left_diverse = False
        for node in self.children.values():
            lc = node.compute_left_diverse()
            if lc is None:
                self.is_left_diverse = True
            else:
                left_characters.update(lc)
        if len(left_characters) > 1:
            self.is_left_diverse = True
        return None if self.is_left_diverse else left_characters

    def common_substrings(self, V: Dict[int, Tuple[int, Id, Path]]):
        k = self.C  # no. of distinct strings in the subtree
        depth = self.depth
        if depth > V[k][0]:
            for id_, path in self.get_positions():  # pragma: no branch
                # select an arbitrary one (the first)
                # change the path to stop at this node
                V[k] = (depth, id_, Path(path.S, path.start, path.start + depth))
                break
        for child in self.children.values():
            child.common_substrings(V)

    def maximal_repeats(self, a: List[Tuple[int, Path]]):
        if self.is_left_diverse:
            a.append((self.C, Path(self.S, self.start, self.end)))
        for child in self.children.values():
            child.maximal_repeats(a)

    def _to_dot(self, a: List[str]) -> None:
        a.append(f'"{str(self)}" [color=red];\n')
        if self.suffix_link is not None:
            a.append(f'"{str(self)}" -> "{str(self.suffix_link)}"')
            a.append(" [color=blue; constraint=false];\n")
        for key, child in self.children.items():
            a.append(f'"{str(self)}" -> "{str(child)}" [label="{str(key)}"];\n')
            child._to_dot(a)


class Leaf(lca_mixin.Leaf, Node):
    """A leaf node.

    Leaf nodes are created when a new suffix is inserted into the tree.

    A suffix tree contains exactly `len(S)` leaf nodes.  A generalized suffix tree
    contains less than `len (concat (S_1..S_N))` leaf nodes.
    """

    __slots__ = ("str_id",)

    def __init__(
        self, parent: Internal, str_id: Id, S: Symbols, start: int, end: int
    ):  # pylint: disable=super-init-not-called
        # super().__init__(parent, S, start, 0)  # Node

        self.parent = parent
        self.S = S
        self.start = start
        self.end = end
        self.depth = end - start
        self.name: str = EMPTY_STR
        self.lca_id = 0
        self.I = 0
        self.A = 0

        self.str_id: Id = str_id
        """The id of the sequence that created this node."""

    def __str__(self) -> str:
        # start + 1 makes it Gusfield-compatible
        # for easier comparing with examples in the book
        return (
            "Leaf '"
            + (self.name or " ".join(map(str, self.S[self.start : self.end])))
            + super().__str__()
            + f"' ({str(self.str_id)}:{self.start + 1})"
        )

    def pre_order(self, f) -> None:
        f(self)

    def post_order(self, f) -> None:
        f(self)

    def add_position(self, l: List[Tuple[Id, Path]]) -> None:
        l.append((self.str_id, Path(self.S, self.start, self.end)))

    def compute_C(self) -> Set[Id]:
        return set([self.str_id])

    def compute_left_diverse(self):
        return [self.S[self.start - 1]] if self.start else None

    def maximal_repeats(self, a: list):
        return

    def _to_dot(self, a: List[str]) -> None:
        a.append(f'"{str(self)}" [color=green];\n')


class UkkonenLeaf(Leaf):
    """A leaf node.

    UkkonenLeaf nodes have mutable ends. See: :attr:`end`.

    A suffix tree contains exactly `len(S)` leaf nodes.  A generalized suffix tree
    contains less than `len (concat (S_1..S_N))` leaf nodes.
    """

    def __init__(
        self, parent: "Internal", str_id: Id, S: Symbols, start: int, end: List[int]
    ):  # pylint: disable=super-init-not-called
        # super().__init__(parent, S, start, 0)  # Node

        self.parent = parent
        self.S = S
        self.start = start
        self.name: str = EMPTY_STR
        self.lca_id = 0
        self.I = 0
        self.A = 0

        self.str_id: Id = str_id
        """The id of the sequence that created this node."""

    @property
    def end(self) -> int:  # type: ignore
        r"""Return the end of the path.

        This is a calculated property because in Ukkonen's algorithm the end of a leaf
        node is implicitly assumed to be the end of the current phase.

        "Any transition of `STree(T_{i-1})` leading to a leaf is called an *open
        transition.*  Such a transition is of the form `g'(s,(k,i-1)) = r` where, as
        stated above, the right pointer has to point to the last position `i-1` of
        `T_{i-1}`. Therefore it is not necessary to represent the actual value of the
        right pointer. Instead, open transitions are represented as `g'(s,(k,\infty)) =
        r` where `\infty` indicates that this transition is 'open to grow'."

        -- [Ukkonen1995]_

        This will return the current length since at the start of each phase we pop a
        symbol off the iterable and append it to self.S.
        """
        return len(self.S)

    @property
    def depth(self) -> int:  # type: ignore
        """Return the string-depth of this node.

        That is the length of the label on the edge going into this node.

        **Definition** For any node `v` in a suffix-tree, the *string-depth* of
        `v` is the number of characters in `v`'s label. --- [Gusfield1997]_
        §5.2, page 90f
        """
        return len(self.S) - self.start
