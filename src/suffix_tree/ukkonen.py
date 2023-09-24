r"""A tree builder that uses Ukkonen's Algorithm.

This module implements Ukkonen's algorithm to build a suffix tree in linear time,
adapted to generalized suffix trees.

"""

from typing import Tuple, List

from .util import Id, Symbol, Symbols, IterSymbols, debug, ukko_str
from .node import Node, Internal, UkkonenLeaf
from . import builder, util


class Builder(builder.Builder):
    """Builds the suffix-tree using Ukkonen's Algorithm."""

    name = "Ukkonen"

    __slots__ = ["aux", "root", "S"]

    def __init__(self):
        super().__init__()
        self.aux: Internal
        self.S: Symbols

    def debug_dot(self, k: int, p: int) -> None:
        """Write a debug graph."""
        self.root.debug_dot(f"/tmp/suffix_tree_ukkonen_{self.id}_{k}_{p}.dot")

    def transition(self, s: Internal, k: int) -> Tuple[Node, Symbols, int, int]:
        """Follow the `s,S,k` transition.

        Let `g'(s,(k',p')) = s'` be the `t_k`-transition from `s`.

        :param node.Internal s: the state `s`
        :param int k: `k`

        :return tuple: `s,S,k,p`
        """
        assert isinstance(s, Internal)
        assert k >= 0

        if s is self.aux:
            # equivalent to *Algorithm 2* line 2
            return self.root, self.S, 0, 1

        s_prime = s.children[self.S[k]]
        return s_prime, s_prime.S, s_prime.start + s.depth, s_prime.end

    def test_and_split(
        self, s: Internal, start: int, end: int, t: Symbol
    ) -> Tuple[bool, Internal]:
        """Test if endpoint and eventually split a transition.

        Return True, if s is the end point.

        "Tests whether or not a state with canonical reference pair `(s,(k,p))` is the
        end point, that is, a state that in `STrie(T^{i-1})` would have a
        `t_i`-transition.  Symbol `t_i` is given as input parameter `t`.  The test
        result is returned as the first output parameter.  If `(s,(k,p))` is not the end
        point, then state `(s,(k,p))` is made explicit (if not already so) by splitting
        a transition.  The explicit state is returned as the second output parameter."
        -- [Ukkonen1995]_
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
            split_depth = s.depth + l
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

    def canonize(self, s: Internal, start: int, end: int) -> Tuple[Internal, int]:
        r"""Canonize a reference pair.

        This has the same function as substep b in McCreight's algorithm.

        "Given a reference pair `(s,(k,p))` for some state `r`, it finds and returns
        state `s'` and left link `k'` such that `(s',(k',p))` is the canonical reference
        pair for `r`.  State `s'` is the closest explicit ancestor of `r` (or `r` itself
        if `r` is explicit).  Therefore the string that leads from `s'` to `r` must be a
        suffix of the string `t_k\dots t_p` that leads from `s` to `r`.  Hence the right
        link `p` does not change but the left link `k` can become `k', k' \geq k`."
        -- [Ukkonen1995]_
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
            s = s_prime  # type: ignore

            if end - start > 0:
                s_prime, _S_prime, k_prime, p_prime = self.transition(s, start)

        if __debug__ and util.DEBUG:
            debug('return s="%s" %s', s, ukko_str(self.S, start, end))
        return s, start

    def update(self, s: Internal, start: int, end: List[int]) -> Tuple[Internal, int]:
        r"""Update the tree.

        "[...] transforms `STree(T^{i-1})` into `STree(T^i)` by inserting the
        `t_i`-transitions in the second group.  The procedure uses procedure canonize
        mentioned above, and procedure test-and-split that tests whether or not a given
        reference pair refers to the end point.  If it does not then the procedure
        creates and returns an explicit state for the reference pair provided that the
        pair does not already represent an explicit state.  Procedure update returns a
        reference pair for the end point `s_{j'}` (actually only the state and the left
        pointer of the pair, as the second pointer remains `i-1` for all states on the
        boundary path)."
        -- [Ukkonen1995]_

        `s,(k,i-1)` is the canonical reference pair for the active
        point.

        :return: a reference pair for the endpoint `s_{j\prime}`.
        """

        assert isinstance(s, Internal)

        i = end[0] - 1

        t_i = self.S[i]
        if __debug__ and util.DEBUG:
            debug('s="%s" %s with "%s"', s, ukko_str(self.S, start, i + 1), t_i)

        old_r = self.root
        is_end_point, r = self.test_and_split(s, start, i, t_i)

        while not is_end_point:
            sstart = i - r.depth

            r_prime = UkkonenLeaf(r, self.id, self.S, sstart, end)
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

    def build(self, root: Internal, id_: Id, S: IterSymbols) -> None:
        """Add a sequence to the tree.

        :param node.Internal root: the root node of the tree
        :param Id id_: the id of the sequence
        :param IterSymbols S: an iterator over the symbols
        """
        self.root = root
        self.id = id_

        # Rearranged a bit from *Algorithm 2* in Ukkonen's paper to include the
        # END symbol in the tree.
        # *Algorithm 2* line 1
        self.aux = Internal(None, [], 0, 0)
        self.aux.name = "aux"
        root.parent = self.aux
        # *Algorithm 2* line 3
        root.suffix_link = self.aux

        mutable_i = [-1]

        # *Algorithm 2* line 4
        s = root
        start = 0
        self.S = []

        # make it tick at step 0 like the other builders
        if self.progress:
            self.progress(0)

        if __debug__ and util.DEBUG:
            debug('string "%s"', str(self.S))

        for i, sym in enumerate(S, start=1):
            self.S.append(sym)

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
