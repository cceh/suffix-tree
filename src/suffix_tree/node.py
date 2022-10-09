"""Node classes for a Generalized Suffix Tree."""

from typing import Optional, cast

from .util import Path, Id, Symbol, Symbols, debug, DEBUG_DOT
from . import lca_mixin, util

EMPTY_STR = ""


class Node(lca_mixin.Node):
    """The abstract base class for internal and leaf nodes."""

    __slots__ = (
        "parent",
        "S",
        "start",
        "_end",
        "name",
    )

    def __init__(self, parent: Optional["Internal"], S: Symbols, start: int, end: int):
        super().__init__()

        self.parent = parent
        """The parent of this node.  Used by Ukkonen and LCA."""

        self.S = S
        """The sequence of symbols. In a generalized tree the first sequence that
        created this node. S[start:end] is the path-label of this node."""
        self.start = start
        """The start position in S of the path-label that goes into this node."""
        self._end = end
        """The end position in S of the path-label that goes into this node."""

        self.name: str = EMPTY_STR
        """A name that can be given to the node.  The name is used only for debugging.
        It is reported in the debug dot graph.
        """

    @property
    def end(self) -> int:
        """Return the end of the path."""
        return self._end

    def depth(self) -> int:
        """Return the string-depth of this node.

        That is the length of the label on the edge going into this node.

        **Definition** For any node :math:`v` in a suffix-tree, the *string-depth* of
        :math:`v` is the number of characters in :math:`v`'s label. --- [Gusfield1997]_
        §5.2, page 90f
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        """Return a string representaion of this node for debugging."""
        raise NotImplementedError()

    def __getitem__(self, i: int) -> Symbol:
        """Return the symol at position i.

        Note: this should implement slices but we don't need them.
        Also we don't need negative indices.
        """
        return self.S[self.start + i]

    def compute_C(self) -> set[Id]:
        """Calculate the :math:`C(v)` number for this node and all its children."""
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

    def add_position(self, l: list[tuple[Id, Path]]) -> None:
        """If this node is a Leaf, then add the path to the list."""
        raise NotImplementedError()

    def get_positions(self) -> list[tuple[Id, Path]]:
        """Get all paths that traverse this node."""
        paths: list[tuple[Id, Path]] = []
        self.pre_order(lambda self_: self_.add_position(paths))
        return paths

    def common_substrings(self, _V: dict[int, tuple[int, Id, Path]]):
        """Common substrings recursive function."""
        return

    def maximal_repeats(self, a: list):
        """Maximal repeats recursive function."""
        raise NotImplementedError()

    def _to_dot(self, a: list[str]) -> None:
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

        if __debug__ and DEBUG_DOT:
            debug("writing dot: %s", filename)
            with open(filename, "w") as tmp:
                tmp.write(self.to_dot())


class Leaf(lca_mixin.Leaf, Node):
    """A leaf node.

    Leaf nodes are created when a new suffix is inserted into the tree.  Leaf nodes have
    mutable ends. See: :py:func:`end`.

    A suffix tree contains exactly :math:`len(S)` leaf nodes.  A generalized suffix tree
    contains less than :math:`len (concat (S_1..S_N))` leaf nodes.
    """

    __slots__ = (
        "_mutable_end",
        "str_id",
    )

    def __init__(
        self, parent: "Internal", str_id: Id, S: Symbols, start: int, end: list[int]
    ):
        # super().__init__(parent, S, start, 0)  # Node

        self.parent = parent
        self.S = S
        self.start = start
        self.name: str = EMPTY_STR
        self.lca_id = 0
        self.I = 0
        self.A = 0

        self._mutable_end: list[int] = end
        """The end position in S of the path-label that goes into this node.
        This is a list of one int so we can 'mutate' the int."""

        self.str_id: Id = str_id
        """The id of the sequence that created this node."""

    @property
    def end(self) -> int:
        """Return the end of the path.

        This is a calculated property because at certain times in Ukkonen's algorithm
        the end of a leaf node is implicitly assumed to be the end of the current phase.

        "**Trick 3**  In phase :math:`i + 1`, when a leaf edge is first created and
        would normally be labeled with substring :math:`S[p..i + 1]`, instead of writing
        indices :math:`(p, i + 1)` on the edge, write :math:`(p, e)` where :math:`e` is
        a symbol denoting "the current end".  Symbol :math:`e` is a *global* index that
        is set to :math:`i + 1` once in each phase."  --- [Gusfield1997]_ §6.1.5 page
        105f

        Basically, :math:`e` is a mutable int, but ints are immutable in Python.  So we
        use instead of :math:`e` a list that contains :math:`e`.  We 'mutate' :math:`e`
        by replacing it in the list with another int.

        """
        return self._mutable_end[0]

    def depth(self) -> int:
        """Return the string depth of this node.

        That is the length of the label on the edge leading into this node.
        """
        return self._mutable_end[0] - self.start

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

    def add_position(self, l: list[tuple[Id, Path]]) -> None:
        l.append((self.str_id, Path(self.S, self.start, self.end)))

    def compute_C(self) -> set[Id]:
        return set([self.str_id])

    def compute_left_diverse(self):
        return [self.S[self.start - 1]] if self.start else None

    def maximal_repeats(self, a: list):
        return

    def _to_dot(self, a: list[str]) -> None:
        a.append(f'"{str(self)}" [color=green];\n')


class Internal(lca_mixin.Internal, Node):
    """An internal node.

    Internal nodes are created for the root and auxiliary node and when splitting edges.
    Internal nodes have at least 2 children and a fixed end.
    """

    __slots__ = (
        "suffix_link",
        "length",
        "children",
        "is_left_diverse",
        "C",
    )

    def __init__(self, parent: Optional["Internal"], S: Symbols, start: int, end: int):
        # save the super call by inlining
        # super().__init__(parent, S, start, end)
        self.parent = parent
        self.S = S
        self.start = start
        self._end = end
        self.name: str = EMPTY_STR
        self.lca_id = 0
        self.I = 0
        self.A = 0

        self.suffix_link: Optional[Internal] = None
        r"""Used by the McCreight and Ukkonen algorithms to speed up the construction of
        the tree.

        "**Corollary 6.1.2** In any implicit suffix tree :math:`\mathcal{T}_i', if
        internal node :math:`v` has path-label :math:`x\alpha`, then *there is* a node
        :math:`s(v)` of :math:`\mathcal{T}_i` with path-label :math:`\alpha`."
        --- [Gusfield1997]_ page 98
        """

        self.length = end - start
        """Cache the length value."""

        self.children: dict[Symbol, Node] = {}
        """ A dictionary of item => node """

        self.is_left_diverse: Optional[bool] = None
        r"""**Definition** A node :math:`v` of :math:`\mathcal{T}` is called *left
        diverse* if at least two leaves in :math:`v`'s subtree have different left
        characters.  By definition a leaf cannot be left diverse.

        For each position :math:`i` in string :math:`S`, character :math:`S(i-1)` is
        called the *left character* of :math:`i`. The *left character of a leaf* of
        :math:`\mathcal{T}` is the left character of the suffix position represented by
        that leaf. --- [Gusfield1997]_ §7.12.1, page 144ff

        N.B. This suffix tree operates on any python hashable object, not just
        characters, so left characters usually are objects.
        """

        self.C: int = -1
        r"""**Definition** For any internal node :math:`v` of :math:`\mathcal{T}`,
        define :math:`C(v)` to be the number of *distinct* string identifiers that
        appear at the leaves in the subtree of :math:`v`. --- [Gusfield1997]_ §7.6, page
        127ff
        """

    def depth(self) -> int:
        """Return the string depth of this node.

        That is the length of the label on the edge going into this node.
        """
        return self.length

    def __str__(self) -> str:
        return (
            "Internal '"
            + (self.name or " ".join(map(str, self.S[self.start : self.end])))
            + "'"
        ) + super().__str__()

    def add_position(self, l: list[tuple[Id, Path]]) -> None:
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
    ) -> tuple["Node", int, Optional["Node"]]:
        """Find a path starting from this node.

        The path is absolute.

        Returns the deepest node on the path, the matched length of the path,
        and also the next deeper node if the matched length is longer than the
        string-depth of the deepest node on the path.
        """
        node: Node = self
        matched_len = self.depth()
        while matched_len < (end - start):
            # find the edge to follow
            assert isinstance(node, Internal)
            child = cast("Internal", node).children.get(S[start + matched_len])
            if child is not None:
                # follow the edge
                stop = min(child.depth(), end - start)
                while matched_len < stop:
                    if child.S[child.start + matched_len] != S[start + matched_len]:
                        break
                    matched_len += 1
                if matched_len < child.depth():
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
        l1 = self.depth()
        l2 = child.depth()
        assert l1 < new_len < l2, f"split length {l1} => {new_len} => {l2}"

        # note: start is the start of the path-label not of the edge-label
        # note: self.end != child.start if self.S != child.S
        new_edge_start = child.start + l1
        new_edge_end = child.start + new_len
        # it is always safe to shorten a path
        new_node = Internal(self, child.S, child.start, new_edge_end)

        self.children[child.S[new_edge_start]] = new_node  # substitute new node
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

    def compute_C(self) -> set[Id]:
        id_set: set[Id] = set()
        for node in self.children.values():
            id_set.update(node.compute_C())
        self.C = len(id_set)
        return id_set

    def compute_left_diverse(self) -> Optional[set]:
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

    def common_substrings(self, V: dict[int, tuple[int, Id, Path]]):
        k = self.C  # no. of distinct strings in the subtree
        depth = self.depth()
        if depth > V[k][0]:
            for id_, path in self.get_positions():  # pragma: no branch
                # select an arbitrary one (the first)
                # change the path to stop at this node
                V[k] = (depth, id_, Path(path, path.start, path.start + depth))
                break
        for child in self.children.values():
            child.common_substrings(V)

    def maximal_repeats(self, a: list[tuple[int, Path]]):
        if self.is_left_diverse:
            a.append((self.C, Path(self.S, self.start, self.end)))
        for child in self.children.values():
            child.maximal_repeats(a)

    def _to_dot(self, a: list[str]) -> None:
        a.append(f'"{str(self)}" [color=red];\n')
        if self.suffix_link is not None:
            a.append(f'"{str(self)}" -> "{str(self.suffix_link)}"')
            a.append(" [color=blue; constraint=false];\n")
        for key, child in self.children.items():
            a.append(f'"{str(self)}" -> "{str(child)}" [label="{str(key)}"];\n')
            child._to_dot(a)
