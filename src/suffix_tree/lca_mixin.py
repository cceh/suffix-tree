r"""A mixin that implements Constant-Time Lowest Common Ancestor Retrieval.

"With the ability to solve lowest common ancestor queries in constant time,
suffix trees can be used to solve many additional string problems."
--- [Gusfield1997]_ §9, 196

"**Definition** In a rooted tree `\mathcal{T}`, a node `u` is an
*ancestor* of a node `v` if `u` is on the unique path from the root
to `v`.  With this definition a node is an ancestor of itself.  A *proper
ancestor* of `v` refers to an ancestor that is not `v`.

**Definition** In a rooted tree `\mathcal{T}`, the *lowest common ancestor
(lca)* of two nodes `x` and `y` is the deepest node in
`\mathcal{T}` that is an ancestor to both `x` and `y`."
--- [Gusfield1997]_ Chapter 8, 181ff
"""

import collections
import ctypes

from . import util
from .util import debug


def uint(x):
    """Convert a number into unsigned 32-bit representation.

    Used only for debugging.
    """

    return ctypes.c_uint32(x).value


def nlz(x):
    """Get the number of leadings zeros in a 32 bit word.

    >>> nlz(0)
    32
    >>> nlz(0x1)
    31
    >>> nlz(0xFF)
    24
    >>> nlz(0xFFFFFFFF)
    0

    See: http://www.hackersdelight.org/hdcodetxt/nlz.c.txt

    See: [Warren2013]_ pages 99ff
    """
    n = 32
    for shift in (16, 8, 4, 2, 1):
        y = x >> shift
        if y != 0:
            n = n - shift
            x = y
    return n - x


def msb(x):
    """Get the position of the most dignificat bit.

    Get the position of the most significant set bit counting from the right and
    starting from 0.

    >>> msb(0xF)
    3
    >>> msb(0xFF)
    7
    >>> msb(0)
    -1

    """
    return 31 - nlz(x)


def h(k):
    r"""Return the h value.

    "**Definition** For any number `k`, `h(k)` denotes the position
    (counting from the right) of the least-significant 1-bit in the binary
    representation of `k`." --- [Gusfield1997]_ §8.5, 184ff

    "**Lemma 8.5.1.** For any node `k` (node with path number k) in
    `\mathcal{B}`, `h(k)` equals the height of node `k` in
    `\mathcal{B}`.

    For example, node 8 (binary 1000) is at height 4, and the path from it to a
    leaf has four nodes (three edges)." --- [Gusfield1997]_ §8.5, 184ff

    N.B. in this implementation we start counting with 0, so you get:

    >>> h(5)
    0
    >>> h(8)
    3

    """
    return 32 - nlz(~k & (k - 1))


# pylint: disable=no-member


class Node:
    """Mixin for Node to allow LCA retireval."""

    __slots__ = "lca_id", "I", "A"

    def __init__(self):  # pragma: no cover
        """This is inlined on all subclasses to save one __init__ call per symbol."""

        self.lca_id = 0
        """Number of the node given in a depth-first traversal of the tree, starting
        with 1.  See [Gusfield1997]_ Figure 8.1, 182
        """

        self.I = 0
        r"""For a node `v` of `\mathcal{T}`, let `I(v)` be a node
        `w` in `\mathcal{T}` such that `h(w)` is maximum over
        all nodes in the subtree of `v` (including `v` itself).
        --- [Gusfield1997]_ §8.5, 184ff

        For any node `v`, node `I(v)` is the deepest node in the run
        containing node `v`. --- [Gusfield1997]_ Lemma 8.6.1., 187

        N.B. This is the id of the node `I(v)`.

        """

        self.A = 0
        r"""Bit `A_v(i)` is set to 1 if and only if node `v` has some
        ancestor in `\mathcal{T}` that maps to height `i` in
        `\mathcal{B}`, i.e. if and only if `v` has an ancestor
        `u` such that `h(I(u))=i`. --- [Gusfield1997]_ §8.7, 188f

        N.B. A node is an ancestor of itself. --- [Gusfield1997]_ §8.1, 181
        """

    def compute_A(self, A):
        """Compute A."""
        raise NotImplementedError()

    def compute_I_and_L(self, L):
        """Compute I and L."""
        raise NotImplementedError()

    def prepare_lca(self, counter):
        """Prepare the node for LCA retrievals."""
        raise NotImplementedError()


class Leaf(Node):
    """A mixin for leaf nodes to allow for LCA retrievals."""

    def __str__(self):
        if __debug__ and util.DEBUG_LABELS:
            # pylint: disable=consider-using-f-string
            return "\n%dh%d I=%dh%d A=0x%x\n" % (
                self.lca_id,
                h(self.lca_id),
                self.I,
                h(self.I),
                self.A,
            )
        return ""

    def compute_A(self, A):
        """Compute A."""
        A |= 1 << h(self.I)
        self.A = A

    def compute_I_and_L(self, L):
        """Compute I and L."""
        self.I = self.lca_id
        L[self.I] = self  # will be overwritten by the highest node in run
        return self.I

    def prepare_lca(self, counter):
        """Prepare the leaf node for LCA retrieval."""
        self.lca_id = counter
        return counter + 1


class Internal(Node):
    """A mixin for internal nodes to allow for LCA retrievals."""

    def __str__(self):
        if __debug__ and util.DEBUG_LABELS:
            # pylint: disable=consider-using-f-string
            return "\n%dh%d I=%dh%d A=0x%x\n" % (
                self.lca_id,
                h(self.lca_id),
                self.I,
                h(self.I),
                self.A,
            )
        return ""

    def compute_A(self, A):
        """Compute A."""
        A |= 1 << h(self.I)
        self.A = A
        for child in self.children.values():
            child.compute_A(A)

    def compute_I_and_L(self, L):
        """Compute I and L."""
        # Find the node with the maximum I value in the subtree.
        imax = self.lca_id
        for child in self.children.values():
            ival = child.compute_I_and_L(L)
            if h(ival) > h(imax):
                imax = ival
        self.I = imax
        L[imax] = self  # will be overwritten by the highest node in run
        return imax

    def prepare_lca(self, counter):
        """Prepare the internal node for LCA retrieval."""
        self.lca_id = counter
        counter += 1
        for dest in self.children.values():
            counter = dest.prepare_lca(counter)
        return counter


class Tree:
    """A mixin for suffix trees to allow for LCA retrievals."""

    def __init__(self, _d):
        self.L = None

        self.nodemap = collections.defaultdict(dict)
        """ map from string position to leaf node """

    def prepare_lca(self):
        """Preprocess the tree for Lowest Common Ancestor retrieval.

        [Gusfield1997]_ §8.7
        """
        self.L = {}
        self.root.prepare_lca(1)
        self.root.compute_I_and_L(self.L)
        self.root.compute_A(0)

        # compute nodemap
        def func(node):
            """Compute a nodemap."""
            if isinstance(node, Leaf):
                self.nodemap[node.str_id][node.start] = node

        self.root.pre_order(func)

    def lca(self, x, y):
        """Return the lowest common ancestor node of nodes x and y.

        >>> from suffix_tree import Tree
        >>> tree = Tree({"A": "xabxac", "B": "awyawxawxz"})
        >>> tree.prepare_lca()
        >>> tree.lca(tree.nodemap["A"][1], tree.nodemap["B"][3]).lca_id
        8
        """
        if x == y:
            return x

        # step 1 - §8.4, §8.8
        k = msb(x.I ^ y.I)
        if __debug__ and util.DEBUG:
            debug("k = msb (%d ^ %d = %d) = %d", x.I, y.I, x.I ^ y.I, k)
        # leave the msb 1-bit and zero all lower bits
        mask = ~0 << (k + 1)  # reset the k + 1 lowest bits in mask
        if __debug__ and util.DEBUG:
            debug("x.I = %d, mask 0x%x", x.I, uint(mask))
        b = (x.I & mask) | (1 << k)  # b = lca (x, y) in B
        if __debug__ and util.DEBUG:
            debug("b = %d, h(b) = %d", b, h(b))

        # step 2 - §8.8
        mask = ~0 << h(b)  # reset the h(b) lowest bits in mask
        if __debug__ and util.DEBUG:
            debug("x.A = 0x%x, y.A = 0x%x, mask = 0x%x", x.A, y.A, uint(mask))
        j = h(x.A & y.A & mask)  # j = h(I(z))
        if __debug__ and util.DEBUG:
            debug("j = %d", j)

        # step 3 and 4
        def get_xy_bar(n):
            r"""Compute `\bar{x}` from `x`."""
            l = h(n.A)
            if l == j:
                return n
            mask = ~(~0 << j)  # set the j lowest bits in mask
            k = msb(n.A & mask)
            mask = ~0 << (k + 1)  # reset k + 1 lowest bits in mask
            Iw = (n.I & mask) | (1 << k)
            if __debug__ and util.DEBUG:
                debug("Iw = %d", Iw)
                debug("L[Iw] = %d", self.L[Iw].lca_id)
            w = self.L[Iw]
            return w.parent

        xbar = get_xy_bar(x)
        ybar = get_xy_bar(y)
        if __debug__ and util.DEBUG:
            debug("xbar = %d, ybar = %d", xbar.lca_id, ybar.lca_id)

        # step 5
        if xbar.lca_id < ybar.lca_id:
            return xbar
        return ybar
