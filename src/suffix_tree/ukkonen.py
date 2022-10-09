r"""A tree builder that uses Ukkonen's Algorithm.

This module implements Ukkonen's algorithm to build a suffix tree in linear time,
adapted to generalized suffix trees.

Some annotations to Ukkonen's paper follow:

Ukkonen identifies subsequences by two indices: :math:`k` and :math:`p`.  In a
generalized suffix tree these are not sufficient to uniquely identify a subsequence, we
also need to know to which sequence :math:`k` and :math:`p` are referring.  So instead
of using the Ukkonen's parameter pair :math:`(k, p)` we use three parameters: :math:`(S,
k, p)`. We also prefer to name them: ``S, start, end``.

We also have two problems with indices:  The first is that Python indices start
with 0 while Ukkonen's start with 1.  The second is that Python indices point to
one beyond the end while Ukkonen's point to the end.  In conclusion: Ukkonen's
:math:`1..2` becomes Python's ``[0:2]``.

Ukkonen treats the *suffix trie* as an automaton and thus uses *state* :math:`s` to
describe what a mere mortal would call a node.  Edges in a trie are labeled by one
character only.  A *branching state* is an internal node, a *final state* is a leaf
node.  Every node in the trie represents a substring and every leaf node represents a
suffix.  The converse is true.  The node representing the string :math:`abc` is called
:math:`\overline{abc}`.

A *suffix tree* is a compressed suffix trie without those internal nodes that have only
one child.  Edges in a tree are labeled by more than one character.  As a consequence
those states in the trie that had their nodes removed become *implicit states* in the
tree.  Those that still retain their nodes are *explicit states*.  Explicit substrings
always end on a node, implicit ones end in the middle of an edge (but can be made
explict by splitting the edge).

States are represented by the triple: :math:`(s, (k, p))`, which is a node and a
substring going out of the node.  There may be more than one such representations.
Remember that we use ``node, S, start, end`` instead.

The *canonical representation* of a state is: the state itself and an empty substring if
explicit, the nearest node above the state and the shortest possible substring if
implicit.

The *transition function* :math:`g'(s, (k, p)) = r` starts at node :math:`s` and ends at
the state :math:`r`, which may be a node or an implicit state (in the middle of an
edge).

The *suffix function* :math:`f(\bar x) = \bar y` is a link present at each internal
node, that points to another node that encodes the same suffix minus the first symbol.
Following suffix links you get from: cacao -> acao -> cao -> ao -> a -> root -> aux.

An *open transition* is any edge going into a leaf.  A leaf's ``end`` grows
automatically whenever a new symbol is added to the tree.  There's a very simple trick
to do this: all leaf nodes use the same mutable integer as their ``end`` index.  If we
update that integer all leaves see the new value.



.. seealso::

   [Ukkonen1995]_

   Ukkonen's suffix tree algorithm in plain English
   https://stackoverflow.com/questions/9452701/

"""

from typing import cast

from .util import Path, Id, Symbol, Symbols, debug, ukko_str
from .node import Node, Internal, Leaf
from . import builder, util


class Builder(builder.Builder):
    """Builds the suffix-tree using Ukkonen's Algorithm."""

    name = "Ukkonen"

    __slots__ = ["aux", "root", "S"]

    def debug_dot(self, k: int, p: int) -> None:
        """Write a debug graph."""
        self.root.debug_dot(f"/tmp/suffix_tree_ukkonen_{self.id}_{k}_{p}.dot")

    def transition(self, s: Internal, k: int) -> tuple[Node, Symbols, int, int]:
        """Let :math:`g'(s,(k',p')) = s'` be the :math:`t_k`-transition from :math:`s`.

        return :math:`s', path'`
        """
        assert isinstance(s, Internal)
        assert k >= 0

        if s is self.aux:
            # equivalent to *Algorithm 2* line 2
            return self.root, self.S, 0, 1

        s_prime = s.children[self.S[k]]
        return s_prime, s_prime.S, s_prime.start + s.depth(), s_prime.end

    def test_and_split(
        self, s: Internal, start: int, end: int, t: Symbol
    ) -> tuple[bool, Internal]:
        """Test if endpoint and eventually split a transition.

        Return True, if s is the end point.

        "Tests whether or not a state with canonical reference pair :math:`(s, (k,
        p))` is the end point, that is, a state that in :math:`STrie(T^{i-1})`
        would have a :math:`t_i`-transition.  Symbol :math:`t_i` is given as
        input parameter :math:`t`.  The test result is returned as the first
        output parameter.  If :math:`(s, (k, p))` is not the end point, then
        state :math:`(s, (k, p))` is made explicit (if not already so) by
        splitting a transition.  The explicit state is returned as the second
        output parameter." --- [Ukkonen1995]_
        """

        assert isinstance(s, Internal)

        if __debug__ and util.DEBUG:
            debug('s="%s" %s t="%s"', s, ukko_str(self.S, start, end), t)
        l = end - start
        if l > 0:
            s_prime, S_prime, k_prime, _p_prime = self.transition(s, start)

            if t == S_prime[k_prime + l]:
                if __debug__ and util.DEBUG:
                    debug('not split 1 return True, node "%s"', s)
                return True, s
            split_depth = s.depth() + l
            r = s.split_edge(split_depth, s_prime)
            if __debug__ and util.DEBUG:
                debug('SPLIT! return False, new node "%s"', r)
            return False, r
        if s is self.aux:
            if __debug__ and util.DEBUG:
                debug('not split 2 return True, node "%s"', s)
            return True, s
        if t in s.children:
            if __debug__ and util.DEBUG:
                debug('not split 3 return True, node "%s"', s)
            return True, s
        if __debug__ and util.DEBUG:
            debug('not split 4 return False, node "%s"', s)
        return False, s

    def canonize(self, s: Internal, start: int, end: int) -> tuple[Internal, int]:
        r"""Canonize a reference pair.

        "Given a reference pair :math:`(s, (k, p))` for some state :math:`r`, it finds
        and returns state :math:`s'` and left link :math:`k'` such that :math:`(s', (k',
        p))` is the canonical reference pair for :math:`r`.  State :math:`s'` is the
        closest explicit ancestor of :math:`r` (or :math:`r` itself if :math:`r` is
        explicit).  Therefore the string that leads from :math:`s'` to :math:`r` must be
        a suffix of the string :math:`t_k\dots t_p` that leads from :math:`s` to
        :math:`r`.  Hence the right link :math:`p` does not change but the left link
        :math:`k` can become :math:`k', k' \geq k`."  --- [Ukkonen1995]_
        """

        assert isinstance(s, Internal)
        if __debug__ and util.DEBUG:
            debug('input  s="%s" %s', s, ukko_str(self.S, start, end))

        l = end - start
        if l == 0:
            if __debug__ and util.DEBUG:
                debug("return unchanged")
            return s, start

        # follow transitions starting from s until we get too far down the tree,
        # then return the transition before the one that went too far
        s_prime, _S_prime, k_prime, p_prime = self.transition(s, start)

        while p_prime - k_prime <= end - start:
            # while the found transition ends higher on the tree, see if the
            # next transition would lead us too far down the tree
            start += p_prime - k_prime
            assert isinstance(s_prime, Internal)
            s = cast(Internal, s_prime)

            if end - start > 0:
                s_prime, _S_prime, k_prime, p_prime = self.transition(s, start)

        if __debug__ and util.DEBUG:
            debug('return s="%s" %s', s, ukko_str(self.S, start, end))
        return s, start

    def update(self, s: Internal, start: int, end: list[int]) -> tuple[Internal, int]:
        r"""Update the tree.

        "[...] transforms :math:`STree(T^{i-1})` into :math:`STree(T^i)` by inserting
        the :math:`t_i`-transitions in the second group.  The procedure uses
        procedure canonize mentioned above, and procedure test-and-split that
        tests whether or not a given reference pair refers to the end point.  If
        it does not then the procedure creates and returns an explicit state for
        the reference pair provided that the pair does not already represent an
        explicit state.  Procedure update returns a reference pair for the end
        point :math:`s_{j'}` (actually only the state and the left pointer of
        the pair, as the second pointer remains :math:`i - 1` for all states on
        the boundary path)." --- [Ukkonen1995]_

        :math:`s,(k,i - 1)` is the canonical reference pair for the active
        point.

        :return: a reference pair for the endpoint :math:`s_{j\prime}`.
        """

        assert isinstance(s, Internal)

        i = end[0] - 1

        t_i = self.S[i]
        if __debug__ and util.DEBUG:
            debug('s="%s" %s with "%s"', s, ukko_str(self.S, start, i + 1), t_i)

        old_r = self.root
        is_end_point, r = self.test_and_split(s, start, i, t_i)

        while not is_end_point:
            sstart = i - r.depth()

            r_prime = Leaf(r, self.id, self.S, sstart, end)
            if __debug__ and util.DEBUG:
                debug('adding leaf "%s"', str(r_prime))
            r.children[t_i] = r_prime

            if old_r is not self.root:
                old_r.suffix_link = r
            old_r = r

            assert isinstance(s, Internal)
            assert s.suffix_link is not None, f'Node "{s}" has no suffix link'
            if __debug__ and util.DEBUG:
                debug(f"follow suffix_link to node {s.suffix_link}")
            if __debug__ and util.DEBUG_DOT:
                self.debug_dot(start, i)

            s, start = self.canonize(s.suffix_link, start, i)
            is_end_point, r = self.test_and_split(s, start, i, t_i)

        if old_r is not self.root:
            old_r.suffix_link = s

        if __debug__ and util.DEBUG_DOT:
            self.debug_dot(start, i)

        if __debug__ and util.DEBUG:
            debug("return node %s k=%d", s, start)
        return s, start

    def build(self, root: Internal, id_: Id, S: Symbols) -> None:
        """Add a sequence to the tree.

        :param node.Internal root: the root node of the tree
        :param Id id_: the id of the sequence
        :param Symbols S: the sequence to insert
        """
        super().build(root, id_, S)

        # Rearranged a bit from *Algorithm 2* in Ukkonen's paper to include the
        # END symbol in the tree.
        # *Algorithm 2* line 1
        self.aux = Internal(None, [], 0, 0)
        self.aux.name = "aux"
        root.parent = self.aux
        # *Algorithm 2* line 3
        root.suffix_link = self.aux

        if __debug__ and util.DEBUG:
            debug('string "%s"', str(self.S))

        mutable_i = [-1]

        # *Algorithm 2* line 4
        s = root
        start = 0
        self.S = []

        # make it compatible with the other builders
        if self.progress:
            self.progress(0)

        for i, sym in enumerate(S):
            self.S.append(sym)
            i += 1

            mutable_i[0] = i

            if __debug__ and util.DEBUG:
                debug(f"enter main loop phase {i}")

            # *Algorithm 2* lines 7, 8
            s, start = self.update(s, start, mutable_i)
            s, start = self.canonize(s, start, i)

            if __debug__ and util.DEBUG:
                debug(
                    'active point is: s="%s" %s',
                    s,
                    ukko_str(self.S, start, i),
                )
                debug(f"exit main loop phase {i}")

            if self.progress and i % self.progress_tick == 0:
                self.progress(i)

        # get rid of the auxiliary node only needed for Ukkonen's algorithm
        # self.root.parent = None  # type: ignore
        # self.root.suffix_link = None
        # self.aux = None
