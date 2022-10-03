"""Node classes for a Generalized Suffix Tree."""

from typing import Optional, cast

from .util import Path, Id, debug
from . import lca_mixin, util

EMPTY_STR = ""


class Node(lca_mixin.Node):
    """The abstract base class for internal and leaf nodes."""

    __slots__ = (
        "parent",
        "suffix_link",
        "path",
        "name",
    )

    def __init__(self, parent, path, **kw):
        super().__init__(parent, path, **kw)

        self.parent: Internal = parent
        """ The parent of this node.  Used by Ukkonen and LCA. """

        self.suffix_link: Optional[Internal] = None
        """ Used by the Ukkonen algorithm while constructing the tree. """

        self.path: Path = path
        """One arbitrarily selected path that traverses this node. (Usually the first
        one in tree construction order.)
        """

        self.name: str = kw.get("name", EMPTY_STR)
        """ A name can be given to the node for easier debugging. """

    def string_depth(self) -> int:
        """Return the string depth of this node.

        "For any node :math:`v` in a suffix-tree, the *string-depth* of :math:`v` is
        the number of characters in :math:`v`'s label."  [Gusfield1997]_ §5.2, 90f
        """
        return len(self)

    def __str__(self) -> str:
        raise NotImplementedError()

    def __len__(self) -> int:
        """We define the length of a node as its string depth."""
        return len(self.path)

    def is_leaf(self) -> bool:
        """Return True if the node is a leaf node."""
        return False

    def compute_C(self) -> set[Id]:
        """Calculate :math:`C(v)` numbers for all nodes."""
        raise NotImplementedError()

    def compute_left_diverse(self):
        """Calculate the left_diversity of this node."""
        raise NotImplementedError()

    def pre_order(self, f) -> None:
        """Walk the tree in visiting each node before its children."""
        raise NotImplementedError()

    def post_order(self, f) -> None:
        """Walk the tree in visiting each node after its children."""
        raise NotImplementedError()

    def get_positions(self) -> list[tuple[Id, "Leaf"]]:
        """Get all paths that traverse this node."""

        paths = []

        def f(node):
            """Append position to paths."""
            if node.is_leaf():
                paths.append((node.str_id, node.path))

        self.pre_order(f)
        return paths

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
            (self.name or str(self.path))
            + super().__str__()
            + f" {str(self.str_id)}:{self.path.start + 1}"
        )

    def is_leaf(self) -> bool:
        """Return True."""
        return True

    def pre_order(self, f) -> None:
        """Traverse the node in pre-order."""
        f(self)

    def post_order(self, f) -> None:
        """Traverse the node in post-order."""
        f(self)

    def compute_C(self) -> set[Id]:
        """Compute C."""
        self.C = 1
        return set([self.str_id])

    def compute_left_diverse(self):
        """See description in Node."""
        return [self.path.S[self.path.start - 1]] if self.path.start else None

    def maximal_repeats(self, a: list):
        """Maximal repeats recursive function."""
        return

    def to_dot(self, a: list[str]) -> None:
        """Translate the node into Graphviz .dot format."""
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
        r"""A node :math:`v` of :math:`\mathcal{T}` is called *left diverse* if at least
        two leaves in :math:`v`'s subtree have different left characters.  By
        definition a leaf cannot be left diverse.  [Gusfield1997]_ §7.12.1,
        144ff

        For each position :math:`i` in string :math:`S`, character
        :math:`S(i-1)` is called the *left character* of :math:`i`. The *left
        character of a leaf* of :math:`\mathcal{T}` is the left character of the
        suffix position represented by that leaf.  [Gusfield1997]_ §7.12.1,
        144ff

        N.B. This suffix tree operates on any python hashable object, not just
        characters, so left_characters usually are objects.
        """

        self.C: int = -1
        r"""For any internal node :math:`v` of :math:`\mathcal{T}`, define :math:`C(v)`
        to be the number of *distinct* string identifiers that appear at the
        leaves in the subtree of :math:`v`.  [Gusfield1997]_ §7.6, 127ff
        """

    def __str__(self) -> str:
        return (self.name or str(self.path)) + super().__str__()

    def pre_order(self, f) -> None:
        """Traverse the node in pre-order."""
        f(self)
        for node in self.children.values():
            node.pre_order(f)

    def post_order(self, f) -> None:
        """Traverse the node in post-order."""
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
                length = path.compare(child.path, matched_len)
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
        p1 = self.path
        p2 = child.path
        assert (
            len(p1) < new_len < len(p2)
        ), f"split length {len(p1)}->{new_len}->{len(p2)}"
        edge_start = p2.start + len(p1)
        edge_end = p2.start + new_len
        # it is always safe to shorten a path
        new_node = Internal(self, Path(p2, p2.start, edge_end))

        self.children[p2.S[edge_start]] = new_node  # substitute new node
        new_node.children[p2.S[edge_end]] = child
        child.parent = new_node

        if __debug__ and util.DEBUG:
            debug("Splitting %s:%s", str(self), str(child))
            debug(
                "Split Adding %s to node %s as [%s]",
                str(new_node),
                str(self),
                p2.S[edge_start],
            )

        return new_node

    def compute_C(self) -> set[Id]:
        """Compute C."""
        id_set: set[Id] = set()
        for node in self.children.values():
            id_set.update(node.compute_C())
        self.C = len(id_set)
        return id_set

    def compute_left_diverse(self) -> Optional[set]:
        """See the description in Node."""
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

    def maximal_repeats(self, a: list[tuple[int, Path]]):
        """Return the maximal repeats."""
        if self.is_left_diverse:
            a.append((self.C, self.path))
        for child in self.children.values():
            child.maximal_repeats(a)

    def to_dot(self, a: list[str]) -> None:
        """Translate the node into Graphviz .dot format."""
        a.append(f'"{str(self)}" [color=red];\n')
        super().to_dot(a)
        for key, child in self.children.items():
            a.append(f'"{str(self)}" -> "{str(child)}" [label="{str(key)}"];\n')
            child.to_dot(a)
