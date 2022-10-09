r"""A tree builder that uses McCreight's Algorithm.

.. |S|     replace:: :math:`\bf S`
.. |Ti+1|  replace:: :math:`T_{\imath+1}`
.. |Ti|    replace:: :math:`T_{\imath}`
.. |Ti-1|  replace:: :math:`T_{\imath-1}`
.. |Ti-2|  replace:: :math:`T_{\imath-2}`
.. |suf|     replace:: :math:`\suf{}`
.. |sufi|    replace:: :math:`\suf{\imath}`
.. |sufi-1|  replace:: :math:`\suf{\imath-1}`
.. |sufj|    replace:: :math:`\suf{\jmath}`
.. |sufj-1|  replace:: :math:`\suf{\jmath-1}`
.. |head|    replace:: :math:`\head{}`
.. |headi|   replace:: :math:`\head{\imath}`
.. |headi-1| replace:: :math:`\head{\imath-1}`
.. |headi+1| replace:: :math:`\head{\imath+1}`
.. |tail|    replace:: :math:`\tail{}`
.. |taili|   replace:: :math:`\tail{\imath}`
.. |taili-1| replace:: :math:`\tail{\imath-1}`

.. |alpha| replace:: :math:`\bs\alpha`
.. |beta|  replace:: :math:`\bs\beta`
.. |gamma| replace:: :math:`\bs\gamma`
.. |delta| replace:: :math:`\bs\delta`
.. |rho|   replace:: :math:`\bs\rho`
.. |chi|   replace:: :math:`\bs\chi`
.. |x|     replace:: :math:`\bf x`
.. |alphabeta|      replace:: :math:`\bs{\alpha\beta}`
.. |alphabetagamma| replace:: :math:`\bs{\alpha\beta\gamma}`
.. |chialpha|       replace:: :math:`\bs{\chi\alpha}`
.. |chialphabeta|   replace:: :math:`\bs{\chi\alpha\beta}`
.. |xdelta|         replace:: :math:`\bf x\bs{\delta}`

The original and mathematically precise exposition (in blockquotes) is taken from the
excellent paper by McCreight [McCreight1976]_.  The comments are by me, trying to
understand the paper and translate it into language suited for mere mortals.

First a few definitions:

    partial path
        A partial path is defined as a (downward) connected sequence of tree arcs which
        begins at the root of the tree.

    path
        A path is defined as a partial path which terminates at a terminal node.

    locus
        The locus of a string is the node at the end of the partial path (if any) named
        by the string.

    extension
        An extension of a string |alpha| is any string of which |alpha| is a prefix.

    extended locus
        The extended locus of a string |alpha| is the locus of the shortest extension of
        |alpha| whose locus is defined.

    contracted locus
        The contracted locus of a string |alpha| is the locus of the longest prefix of
        |alpha| whose locus is defined.

    |sufi|
        is the suffix of |S| beginning at character position :math:`i` (beginning with
        1).

    |headi|
        We define |headi| as the longest prefix of |sufi| which is also a prefix of
        :math:`\suf{j}` for some :math:`j < i`. Equivalently, |headi| is the longest
        prefix of |sufi| whose extended locus exists within the tree |Ti-1|.

    |taili|
        We define |taili| as :math:`\suf{\imath}-\head{\imath}`.


The McCreight algorithm inserts all suffixes of |S| in order beginning with the longest.

To insert one suffix |suf|, we search the tree from the root until we get a mismatch. If
the mismatch happens on a node, we call that node the |head|. If the mismatch happens in
the middle of an edge, we split the edge and insert a new node, and call this new node
the |head|.  Then we append the |tail| to the |head|. For each suffix we create exactly
one leaf node and at most one internal node.

This procedure is slow because we have to search starting from the root over and over
again.  McCreight's invention is how to jump from |headi-1| to |headi| in linear time.

Consider that:  If |headi-1| can be written as |xdelta| (where |x| is a character and
|delta| is a string), then the search for |headi| cannot end before having passed
through |delta|. The locus |delta| will be created if it does not yet exist.

PROOF: |headi-1| can exists only if two suffixes |sufj-1| and |sufi-1| diverged at
|xdelta|.  But then |sufj| and |sufi| too must diverge at |delta|.

    LEMMA 1. If |headi-1| can be written as |xdelta| for some character |x| and some
    (possibly empty) string |delta|, then |delta| is a prefix of |headi|.

    PROOF. By induction on :math:`i`. Suppose :math:`\head{\imath-1}=\bf x\bs{\delta}`.
    This means that there is a :math:`j,\, j < i`, such that |xdelta| is a prefix both
    of |sufi-1| and of |sufj-1|. Thus |delta| is a prefix both of |sufi| and of |sufj|.
    Therefore by the definition of |head|, |delta| is a prefix of |headi|.
    :math:`\quad\square`

It would therefore save time if you could go from |headi-1| to the locus of |delta| and
continue your search for |headi| from there instead of starting at the root every time.

McCreight introduces suffix links.  A **suffix link** is a pointer from the locus
|xdelta| to the locus |delta|.  Unfortunately this link can be created only after the
first time you'd need it, but it will be used to short-circuit all further searches
through locus |xdelta|.

    To exploit this relationship, auxiliary links are added to our tree structure. From
    each nonterminal node which is the locus of |xdelta|, where |x| is a character and
    |delta| is a string, a suffix link is introduced pointing to the locus of |delta|.
    (Note that the locus of |delta| is never within the subtree rooted at the locus of
    |xdelta|.) […]  These links enable the algorithm in step :math:`i` to do a short-cut
    search for the locus of |headi| beginning at the locus of |headi-1| which it has
    visited in the previous step.  The following semiformal presentation of the
    algorithm will prove by induction on :math:`i` that

        :math:`P1`: in tree |Ti| only the locus of |headi| could fail to have a valid
        suffix link, and that

        :math:`P2`: in step :math:`i` the algorithm visits the contracted locus of
        |headi| in |Ti-1|.

    Properties :math:`P1` and :math:`P2` clearly obtain if :math:`i = 1`. Now suppose
    :math:`i > 1`. In step :math:`i` the algorithm does the following:

It follows a description of the algorithm:

Substep A. Let us write down |headi-1| as the concatenation of three strings
|chialphabeta|.  Let us also write down |headi| in the same way as |alphabetagamma|.

|chi| was the first character in |sufi-1| and is of no more importance when we insert
|sufi|.  |alpha| is that part of |sufi| we can short-circuit with a suffix link.  |beta|
is the next part of |sufi| which we can fast-forward by "rescanning".  |gamma| is the
third part of |sufi| for which we have to use slow "scanning". (And |taili| is the last
part of |sufi|.)

We go to the first ancestor-or-self of |headi-1| that has a suffix link.  (That would be
|chialpha|.)  We then follow the suffix link to the locus of |alpha| and call that node
:math:`c`.  Goto substep B.

Note that if we set the suffix link of root to root itself we don't have to special case
an empty |alpha|.

    Substep A. First the algorithm identifies three strings |chi|, |alpha|, and |beta|,
    with the following properties:

      (1) |headi-1| can be represented as |chialphabeta|.

      (2) If the contracted locus of |headi-1| in |Ti-2| is not the root, it is the
          locus of |chialpha|. Otherwise |alpha| is empty.

      (3) |chi| is a string of at most one character which is empty only if |headi+1| is
          empty.

    Lemma 1 guarantees that |headi| may be represented as |alphabetagamma| for some
    (possibly empty) string |gamma|. The algorithm now chooses the appropriate case of
    the following two:

      - |alpha| empty: The algorithm calls the root node :math:`c` and goes to substep
        B.  Note that :math:`c` is defined as the locus of |alpha|.

      - |alpha| nonempty: By definition, the locus of |chialpha| must have existed in
        the tree |Ti-2|. By :math:`P1` the suffix link of that (nonterminal) locus node
        must be defined in tree |Ti-1|, since the node itself must have been constructed
        before step :math:`i - 1`. By :math:`P2` the algorithm visited that node in step
        :math:`i - 1`. The algorithm follows its suffix link to a nonterminal node
        called :math:`c` and goes to substep B. Note that :math:`c` is defined as the
        locus of |alpha|.

Substep B.  From the node :math:`c`, the locus of |alpha|, we search the locus of
|alphabeta|.  We can save time by what McCreight calls "rescanning", because we already
know that all characters in |beta| must match.  If we overshot the length of |beta| we
have to split the edge as usual.  When found, we call that node :math:`d`.  Goto Substep
C.  Note that if |gamma| is not empty the edge will already be split.

    Substep B.  This is called "rescanning," and is the key idea of algorithm M.  Since
    |alphabetagamma| is defined as |headi|, by the definition of |head| we know that the
    extended locus of |alphabeta| exists in the tree |Ti-1|.  This means that there is a
    sequence of arcs downward from node :math:`c` (the locus of |alpha|) which spells
    out some extension of |beta|. To rescan |beta| the algorithm finds the child arc
    |rho| of :math:`c` which begins with the first character of |beta| and leads to a
    node which we shall call :math:`f`.  It compares the *lengths* of |beta| and |rho|.
    If |beta| is longer, then a recursive rescan of :math:`\beta - \rho` is begun from
    node :math:`f`.  If |beta| is the same length or shorter, then |beta| is a prefix of
    |rho|, the algorithm has found the extended locus of |alphabeta| and the rescan is
    complete.  It has been accomplished in time linear in the number of nodes
    encountered.  A new nonterminal node is constructed to be the locus of |alphabeta|
    if one does not already exist.  The algorithm calls :math:`d` the locus of
    |alphabeta| and goes to substep C. (Note that substep B constructs a new node to be
    the locus of |alphabeta| only if |gamma| is empty.)

Substep C.  First we set the suffix link on |chialphabeta| to point to |alphabeta|.
Then from the locus of |alphabeta| we scan the slow way to |alphabetagamma| comparing
each character until we get a mismatch.  If the mismatch happens on a node, we call that
node |headi|. If the mismatch happens in the middle of an edge, we split the edge and
insert a new node, and call the new node |headi|.  Then we append the unmatched rest to
the |headi|.  Increment :math:`i` and goto Substep A.

    Substep C. This is called "scanning." If the suffix link of the locus of
    |chialphabeta| is currently undefined, the algorithm first defines that link to
    point to node :math:`d`. This and inductive hypothesis establish the truth of
    :math:`P1` in |Ti|. Then the algorithm begins searching from node :math:`d` deeper
    into the tree to find the extended locus of |alphabetagamma|. The major difference
    between scanning and rescanning is that in rescanning the length of |beta| is known
    beforehand (because it has already been scanned), while in scanning the length of
    |gamma| is not known beforehand. Thus the algorithm must travel downward into the
    tree in response to the characters of |taili| (of which |gamma| is a prefix) one by
    one from left to right. When the algorithm "falls out of the tree" (as constraint
    :math:`S1` guarantees that it must), it has found the extended locus of
    |alphabetagamma|. The last node of |Ti-1| encountered in this downward trek of
    rescanning and scanning is the contracted locus of |headi| in |Ti-1| ; this
    establishes the truth of :math:`P2`. A new nonterminal node is constructed to be the
    locus of |alphabetagamma| if one does not already exist.  Finally a new arc labeled
    |taili|, is constructed from the locus of |alphabetagamma| to a new terminal node.
    Step :math:`i` is now finished.

..  seealso::

   [McCreight1976]_

   https://www.cs.helsinki.fi/u/tpkarkka/opetus/10s/spa/lectures.pdf
"""

from typing import cast

from .util import Path, Id, Symbols, debug
from .node import Node, Internal, Leaf
from . import builder, util


class Builder(builder.Builder):
    """Builds the suffix-tree using Ukkonen's Algorithm."""

    name = "McCreight"

    __slots__ = ["root"]

    def debug_dot(self, start: int) -> None:
        """Write a debug graph."""
        self.root.debug_dot(f"/tmp/suffix_tree_mccreight_{str(self.id)}_{start}.dot")

    def compute_suffix_link(self, node: Internal) -> Internal:
        r"""Do the suffix-link dance.

        Ascend to parent, follow suffix-link and "rescan" along the suffix path to the
        old depth - 1.  If the path ends in the middle of an edge, split the edge and
        insert a new node.

        :param node.Internal node: |headi-1|, the locus of |chialphabeta|
        :return: the node :math:`d`, the locus of |alphabeta|
        """
        if __debug__ and util.DEBUG:
            debug(f"start of suffix-link dance for node {node} depth={node.depth()}")
        assert node.parent is not None
        assert node.parent.suffix_link is not None

        # ascend to parent, follow suffix-link
        depth = node.depth() - 1
        f: Node = node.suffix_link or node.parent.suffix_link

        # begin of Substep B
        # Rescan along the path to the old depth - 1.
        while f.depth() < depth:
            assert isinstance(f, Internal)
            f = cast(Internal, f).children[node[f.depth() + 1]]
        if f.depth() > depth:
            # Unfortunately the path ended in the middle of an edge, so split the edge.
            assert f.parent
            f = f.parent.split_edge(depth, f)

        if __debug__ and util.DEBUG:
            debug(f"end of suffix-link dance on node {f} depth={f.depth()}")
        assert f.depth() == depth
        assert isinstance(f, Internal)
        return cast(Internal, f)

    def build(self, root: Internal, id_: Id, S: Symbols) -> None:
        r"""Add a sequence to the tree.

        :param node.Internal root: the root node of the tree
        :param Id id_: the id of the sequence
        :param Symbols S: the sequence to insert
        """
        super().build(root, id_, S)

        root.suffix_link = root
        # root.parent = root

        S = list(self.S)  # McCreight is not an online algorithm
        end = len(S)
        node = root

        for start in range(end):
            if self.progress and start % self.progress_tick == 0:
                self.progress(start)

            # find longest path from node
            node, matched_len, child = node.find_path(S, start, end)  # type: ignore

            if child is not None:
                # the path ended in the middle of an edge
                node = node.split_edge(matched_len, child)

            # assert matched_len == node.depth(), f"Add String {matched_len}/{node.depth()}"
            # assert matched_len < (end - start), f"{matched_len} < {end}-{start}"
            # assert S[start + matched_len] not in node.children  # do not overwrite

            new_leaf = Leaf(node, self.id, S, start, [end])
            node.children[S[start + matched_len]] = new_leaf

            if __debug__ and util.DEBUG:
                debug(
                    "Added %s to node %s as [%s]",
                    str(new_leaf),
                    str(node),
                    S[start + node.depth()],
                )
            if __debug__ and util.DEBUG_DOT:
                self.debug_dot(start)

            # Here start McCreights changes from the naive algorithm.  Instead of
            # restarting the search from the root McCreight builds and follows the
            # suffix_link.
            if node.suffix_link is None:
                node.suffix_link = self.compute_suffix_link(node)
            node = node.suffix_link
