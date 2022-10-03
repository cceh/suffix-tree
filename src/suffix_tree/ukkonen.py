r"""A tree builder that uses Ukkonen's Algorithm.

Ukkonen's algorithm to build a suffix tree in linear time adapted to
generalized suffix trees.

In a generalized suffix tree the start and end indices k and p are not enough to
uniquely identify a substring, we also need to keep track which string k and p
are referring to.  So instead of using the three parameters :math:`s, (k, p)` we
use the two parameters s and path, with path being a structure containing
string, k, and p.

We also have two problems with indices:  The first is that Python indices start
with 0 while Ukkonen's start with 1.  The second is that Python indices point to
one beyond the end while Ukkonen's point to the end.  In conclusion: Ukkonen's
1..2 becomes Python's [0:2].


.. [Ukkonen1995] Ukkonen, Esko.  On-line construction of suffix trees.  1995.
                 Algorithmica 14:249-60.
                 http://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf

See also: Ukkonen's suffix tree algorithm in plain English
https://stackoverflow.com/questions/9452701/

"""

from typing import cast

from .util import Path, Id, Symbol, debug, debug_dot
from .node import Node, Internal, Leaf
from . import builder, util


class Builder(builder.Builder):
    """Builds the suffix-tree using Ukkonen's Algorithm."""

    name = "Ukkonen"

    def __init__(self, tree, id_: Id, path: Path):
        super().__init__(tree, id_, path)

        # create the auxiliary node only needed for Ukkonen's algorithm
        aux = Internal(None, Path.from_iterable([]), name="aux")
        self.root.parent = aux
        self.root.suffix_link = aux
        self.aux = aux

    def debug_dot(self, k: int, p: int) -> None:
        """Write a debug graph."""
        debug_dot(self.tree, f"/tmp/suffix_tree_ukkonen_{self.id}_{k}_{p}")

    def transition(self, s: Internal, k: int) -> tuple[Node, Path]:
        """Let :math:`g'(s,(k',p')) = s'` be the :math:`t_k`-transition from :math:`s`.

        return :math:`s', path'`
        """
        assert isinstance(s, Internal)
        assert k >= 0

        if s is self.aux:
            # simulates line 2. from *Algorithm 2*.
            return self.root, Path(self.path, 0, 1)

        s_prime = s.children[self.path[k]]
        path = s_prime.path

        return s_prime, Path(path, path.start + len(s), path.end)

    def test_and_split(
        self, s: Internal, path: Path, t: Symbol
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
        output parameter."  [Ukkonen1995]_
        """

        assert isinstance(s, Internal)

        if __debug__ and util.DEBUG:
            debug('s="%s" %s t="%s"', s, path.ukko_str(), t)
        if path:
            s_prime, path_prime = self.transition(s, path.k)
            if __debug__ and util.DEBUG:
                debug('s\'="%s" %s', s_prime, path_prime.ukko_str())
                debug('path_prime[len (path)] = "%s"', path_prime[len(path)])

            if t == path_prime[len(path)]:
                if __debug__ and util.DEBUG:
                    debug('not split 1 return True, node "%s"', s)
                return True, s
            split_depth = len(s) + len(path)
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

    def canonize(self, s: Internal, path: Path) -> tuple[Internal, Path]:
        r"""Canonize a reference pair.

        "Given a reference pair :math:`(s, (k, p))` for some state :math:`r`, it finds
        and returns state :math:`s'` and left link :math:`k'` such that :math:`(s', (k',
        p))` is the canonical reference pair for :math:`r`.  State :math:`s'` is the
        closest explicit ancestor of :math:`r` (or :math:`r` itself if :math:`r` is
        explicit).  Therefore the string that leads from :math:`s'` to :math:`r` must be
        a suffix of the string :math:`t_k\dots t_p` that leads from :math:`s` to
        :math:`r`.  Hence the right link :math:`p` does not change but the left link
        :math:`k` can become :math:`k', k' \gte k`."  [Ukkonen1995]_
        """

        assert isinstance(s, Internal)
        if __debug__ and util.DEBUG:
            debug('input  s="%s" %s', s, path.ukko_str())

        if not path:
            if __debug__ and util.DEBUG:
                debug("return unchanged")
            return s, path

        # follow transitions starting from s until we get too far down the tree,
        # then return the transition before the one that went too far
        s_prime, path_prime = self.transition(s, path.k)

        while len(path_prime) <= len(path):
            # while the found transition ends higher on the tree, see if the
            # next transition would lead us too far down the tree
            path.start += len(path_prime)
            assert isinstance(s_prime, Internal)
            s = cast(Internal, s_prime)

            if path:
                s_prime, path_prime = self.transition(s, path.k)

        if __debug__ and util.DEBUG:
            debug('return s="%s" %s', s, path.ukko_str())
        return s, path

    def update(self, s: Internal, path: Path) -> tuple[Internal, Path]:
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
        the boundary path)." [Ukkonen1995]_

        :math;`s,(k,i - 1)` is the canonical reference pair for the active
        point.

        Return a reference pair for the endpoint :math:`s_{j\prime}`.
        """

        assert isinstance(s, Internal)

        t_i = self.path[path.i]
        if __debug__ and util.DEBUG:
            debug('s="%s" %s with "%s"', s, path.ukko_str(), t_i)

        act_path = Path(path, path.start, path.end - 1)

        oldr = self.root
        is_end_point, r = self.test_and_split(s, act_path, t_i)

        while not is_end_point:
            start = path.p - len(r)

            r_prime = Leaf(r, self.id, Path(self.path, start, None))
            if __debug__ and util.DEBUG:
                debug('adding leaf "%s"', str(r_prime))
            r.children[t_i] = r_prime

            if oldr is not self.root:
                oldr.suffix_link = r
            oldr = r

            assert isinstance(s, Internal)
            assert s.suffix_link is not None, f'Node "{s}" has no suffix link'
            if __debug__ and util.DEBUG:
                debug(f'follow suffix_link to node "{s.suffix_link}"', s.suffix_link)
            if __debug__ and util.DEBUG_DOT:
                self.debug_dot(act_path.k, act_path.p)

            s, act_path = self.canonize(s.suffix_link, act_path)
            is_end_point, r = self.test_and_split(s, act_path, t_i)

        if oldr is not self.root:
            oldr.suffix_link = s

        if __debug__ and util.DEBUG_DOT:
            self.debug_dot(act_path.k, act_path.p)

        path.start = act_path.start

        if __debug__ and util.DEBUG:
            debug("return node %s k=%d", s, path.k)
        return s, path

    def build(self) -> None:
        """Add a string to the tree."""

        # Rearranged a bit from *Algorithm 2* in Ukkonen's paper to include the
        # END symbol in the tree.

        if __debug__ and util.DEBUG:
            debug('string "%s"', self.path)

        s = self.root
        len_ = len(self.path)

        path = Path(self.path, 0, 1)  # initial path of 1 symbol

        while True:
            if self.progress:
                self.progress(path.end)

            if __debug__ and util.DEBUG:
                debug("enter main loop")

            path.set_open_end(path.end)
            s, path = self.update(s, path)
            s, path = self.canonize(s, path)
            if __debug__ and util.DEBUG:
                debug('active point is: s="%s" %s', s, path.ukko_str())

            if path.end == len_:
                break

            path.end += 1

            if __debug__ and util.DEBUG:
                debug("exit main loop\n")

        # get rid of the auxiliary node only needed for Ukkonen's algorithm
        # self.root.parent = None  # type: ignore
        # self.root.suffix_link = None
        # self.aux = None
