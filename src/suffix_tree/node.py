"""Node classes for a Generalized Suffix Tree."""

from typing import Optional, cast

from .util import Path, Id, Symbol, Symbols, debug
from . import lca_mixin, util

EMPTY_STR = ""


class Node(lca_mixin.Node):
    """The abstract base class for internal and leaf nodes."""

    __slots__ = (
        "parent",
        "suffix_link",
        "_path",
        "name",
    )

    def __init__(self, parent, path, **kw):
        super().__init__(parent, **kw)

        self.parent: Internal = parent
        """The parent of this node.  Used by Ukkonen and LCA."""

        self.suffix_link: Optional[Internal] = None
        """Used by the Ukkonen algorithm while constructing the tree."""

        self._path: Path = path
        """One arbitrarily selected path that traverses this node. (Usually the first
        one in tree construction order.)
        """

        self.name: str = kw.get("name", EMPTY_STR)
        """A name that can be given to the node.  The name is used only for debugging.
        It is reported in the debug dot graph.
        """

    def string_depth(self) -> int:
        """Return the string-depth of this node.

        **Definition** For any node :math:`v` in a suffix-tree, the *string-depth* of
        :math:`v` is the number of characters in :math:`v`'s label. --- [Gusfield1997]_
        §5.2, page 90f
        """
        return len(self)

    def __str__(self) -> str:
        """Return a string representaion of this node for debugging."""
        raise NotImplementedError()

    def __len__(self) -> int:
        """Return the string depth of this node."""
        return len(self._path)

    @property
    def S(self) -> Symbols:
        """Return the start of the path."""
        return self._path.S

    @property
    def start(self) -> int:
        """Return the start of the path."""
        return self._path.start

    @property
    def end(self) -> int:
        """Return the end of the path."""
        return self._path.end

    def __getitem__(self, i: int) -> Symbol:
        """Return the symol at position i.

        Note: this should implement slices but we don't need them.
        Also we don't need negative indices.
        """
        return self._path.S[self._path.start + i]

    def compare(self, other: Path, offset: int = 0) -> int:
        """Compare this node against a path, return the matched length."""
        length = min(len(self), len(other)) - offset
        offset1 = self.start + offset
        offset2 = other.start + offset
        i = 0

        while i < length:
            if self.S[offset1 + i] != other.S[offset2 + i]:
                break
            i += 1
        if __debug__ and util.DEBUG:
            debug(
                "Comparing %s == %s at offsets %d => common len: %d",
                str(self),
                str(other),
                offset,
                i,
            )
        return i

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

    def to_dot(self, a: list[str]) -> None:
        """Translate the node into Graphviz .dot format."""
        if self.suffix_link is not None:
            a.append(f'"{str(self)}" -> "{str(self.suffix_link)}"')
            a.append(" [color=blue; constraint=false];\n")


class Leaf(lca_mixin.Leaf, Node):
    """A leaf node.

    A suffix tree contains exactly len(S) leaf nodes.  A generalized suffix tree
    contains less than len (concat (S_1..S_N)) leaf nodes.

    """

    __slots__ = ("str_id",)

    def __init__(self, parent: Node, str_id: Id, path, **kw):
        super().__init__(parent, path, **kw)  # Node
        self.str_id = str_id

    def __str__(self) -> str:
        # start + 1 makes it Gusfield-compatible
        # for easier comparing with examples in the book
        return (
            (self.name or str(self._path))
            + super().__str__()
            + f" {str(self.str_id)}:{self._path.start + 1}"
        )

    def pre_order(self, f) -> None:
        f(self)

    def post_order(self, f) -> None:
        f(self)

    def add_position(self, l: list[tuple[Id, Path]]) -> None:
        l.append((self.str_id, self._path))

    def compute_C(self) -> set[Id]:
        return set([self.str_id])

    def compute_left_diverse(self):
        return [self._path.S[self._path.start - 1]] if self._path.start else None

    def maximal_repeats(self, a: list):
        return

    def to_dot(self, a: list[str]) -> None:
        a.append(f'"{str(self)}" [color=green];\n')
        super().to_dot(a)


class Internal(lca_mixin.Internal, Node):
    """An internal node.

    Internal nodes have at least 2 children.
    """

    __slots__ = (
        "children",
        "is_left_diverse",
        "C",
    )

    def __init__(self, parent, path, **kw):
        super().__init__(parent, path, **kw)

        self.children: dict[object, Node] = {}
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

    def __str__(self) -> str:
        return (self.name or str(self._path)) + super().__str__()

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

    def find_path(self, path) -> tuple["Node", int, Optional["Node"]]:
        """Find a path starting from this node.

        The path is absolute.

        Returns the deepest node on the path, the matched length of the path,
        and also the next deeper node if the matched length is longer than the
        string-depth of the deepest node on the path.
        """
        node: Node = self
        matched_len = len(node)
        while matched_len < len(path):
            # find the edge to follow
            assert isinstance(node, Internal)
            child = cast("Internal", node).children.get(
                path.S[path.start + matched_len]
            )
            if child:
                # follow the edge
                length = child.compare(path, matched_len)
                # there must be at least one match
                assert (
                    length > 0
                ), f"find_path length={length} matched_len={matched_len}"
                matched_len += length
                if matched_len < len(child):
                    # the path ends between node and child
                    return node, matched_len, child
                # we reached child, loop
                node = child
            else:
                # no edge to follow
                return node, matched_len, None
        # path exhausted
        return node, matched_len, None

    def split_edge(self, new_len: int, child: Node) -> "Internal":
        """Split the edge.

        Split self --> child into self --> new_node --> child and return the new node.
        new_len is the string-depth of the new node.
        """
        l1 = len(self)
        l2 = len(child)
        assert l1 < new_len < l2, f"split length {l1} => {new_len} => {l2}"
        edge_start = child.start + l1
        edge_end = child.start + new_len
        # it is always safe to shorten a path
        new_node = Internal(self, Path(child.S, child.start, edge_end))

        self.children[child.S[edge_start]] = new_node  # substitute new node
        new_node.children[child.S[edge_end]] = child
        child.parent = new_node

        if __debug__ and util.DEBUG:
            debug("Splitting %s:%s", str(self), str(child))
            debug(
                "Split Adding %s to node %s as [%s]",
                str(new_node),
                str(self),
                child.S[edge_start],
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
        sd = self.string_depth()
        if sd > V[k][0]:
            for id_, path in self.get_positions():  # pragma: no branch
                # select an arbitrary one (the first)
                # change the path to stop at this node
                V[k] = (sd, id_, Path(path, path.start, path.start + sd))
                break
        for child in self.children.values():
            child.common_substrings(V)

    def maximal_repeats(self, a: list[tuple[int, Path]]):
        if self.is_left_diverse:
            a.append((self.C, self._path))
        for child in self.children.values():
            child.maximal_repeats(a)

    def to_dot(self, a: list[str]) -> None:
        a.append(f'"{str(self)}" [color=red];\n')
        super().to_dot(a)
        for key, child in self.children.items():
            a.append(f'"{str(self)}" -> "{str(child)}" [label="{str(key)}"];\n')
            child.to_dot(a)
