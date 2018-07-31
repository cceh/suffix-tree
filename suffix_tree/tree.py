# -*- coding: utf-8 -*-
#

"""A Generalized Suffix Tree

See: README.rst.

"""

import collections
import itertools

from . import naive
from . import ukkonen
from . import ukkonen_gusfield
from . import lca_mixin

from .node import Internal
from .util import Path, UniqueEndChar, is_debug

class Tree (lca_mixin.Tree):
    """A suffix tree.

    The key feature of the suffix tree is that for any leaf :math:`i`, the
    concatenation of the edgle-labels on the path from the root to leaf
    :math:`i` exactly spells out the suffix of :math:`S` that starts at point
    :math:`i`.  That is, it spells out :math:`S[i..m]`.

    Initialize and interrogate the tree:

    >>> tree = Tree ({ 'A' : 'xabxac' })
    >>> tree.find ('abx')
    True
    >>> tree.find ('abc')
    False

    >>> tree = Tree ({ 'A' : 'xabxac', 'B' : 'awyawxacxz' })
    >>> for id_, path in tree.find_all ('xac'):
    ...    print (id_, ':', str (path))
    A : x a c $
    B : x a c x z $
    >>> tree.find_all ('abc')
    []

    >>> from . import naive
    >>> tree = Tree ({ 'A' : 'xabxac' }, naive.Builder)
    >>> tree.find ('abx')
    True
    >>> tree.find ('abc')
    False

    """

    def __init__ (self, d, builder = ukkonen.Builder):
        """ Initialize and build the tree from dict of iterables.

        """

        super ().__init__ (d)

        self.root = Internal (None, Path (tuple (), 0, 0), name = 'root')

        for id_, S in d.items ():
            # input is any iterable, make an immutable copy with a unique
            # character at the end
            path = Path.from_iterable (itertools.chain (S, [UniqueEndChar (id_)]))

            self.builder = builder (self, id_, path)

            try:
                self.builder.build ()
            except:
                if is_debug ():
                    with open ('/tmp/core.dot', 'w') as tmp:
                        tmp.write (self.to_dot ())
                raise

    def find_path (self, path):
        """Find a path in the tree.

        Returns the deepest node on the path, the matched length of the path,
        and also the next deeper node if the matched length is longer than the
        string-depth of the deepest node on the path.

        """
        return self.root.find_path (path)

    def find (self, iterable):
        """ Return True if string is found

        >>> tree = Tree ({ 'A' : 'xabxac' })
        >>> tree.find ('abx')
        True
        >>> tree.find ('abc')
        False
        """

        path = Path.from_iterable (iterable)
        dummy_node, matched_len, dummy_child = self.find_path (path)
        return matched_len == len (path)

    def find_all (self, iterable):
        """ Return all indices of path in tree.

        >>> tree = Tree ({ 'A' : 'xabxac' })
        >>> for id_, path in tree.find_all ('ab'):
        ...    print (id_, ':', str (path))
        A : a b x a c $
        >>> tree.find_all ('abc')
        []
        """

        path = Path.from_iterable (iterable)
        node, matched_len, child = self.find_path (path)
        if matched_len < len (path):
            return []
        return (child or node).get_positions ()

    def common_substrings (self):
        """Get a list of common substrings.

        **Definition** For each :math:`k` between 2 and :math:`K`, we define
        :math:`l(k)` to be the length of the *longest substring common to at
        least* :math:`k` *of the strings.*

        Returns a table of :math:`K - 1` entries, where entry :math:`k` gives
        :math:`l(k)`.

        >>> tree = Tree ({'A': 'sandollar', 'B': 'sandlot',
        ...    'C' : 'handler', 'D': 'grand', 'E': 'pantry'})
        >>> for k, length, path in tree.common_substrings ():
        ...    print (k, length, path)
        2 4 s a n d
        3 3 a n d
        4 3 a n d
        5 2 a n

        [Gusfield1997]_ §7.6, 127ff
        """

        self.root.compute_C ()

        V = collections.defaultdict (lambda: (0, 'no_id', None)) # C => (string_depth, id, path)
        def f (node):
            """ Helper """
            k = node.C
            sd = node.string_depth ()
            if sd > V[k][0]:
                for id_, path in node.get_positions ():
                    # select an arbitrary one (the first)
                    # change the path to stop at this node
                    V[k] = (sd, id_, Path (path.S, path.start, path.start + sd))
                    break

        self.root.pre_order (f)

        l = []
        max_len = 0
        max_path = None
        for k in range (max (V.keys ()), 1, -1):
            length = V[k][0]
            if length > max_len:
                max_len = length
                max_path = V[k][2]
            l.append ((k, max_len, max_path))
        return sorted (l)

    def maximal_repeats (self):
        """Get a list of the maximal repeats in the tree.

        N.B.  The repeats must be in different input strings.

        >>> tree = Tree ({ 'A' : 'xabxac', 'B' : 'awyawxawxz' })
        >>> for C, path in sorted (tree.maximal_repeats ()):
        ...    print (C, path)
        1 a w
        1 a w x
        2 a
        2 x
        2 x a

        See [Gusfield1997]_ §7.12.1, 144ff.

        """
        self.root.compute_C ()
        self.root.compute_left_diverse ()

        a = []
        for child in self.root.children.values ():
            child.maximal_repeats (a)
        return a

    def to_dot (self):
        """ Output the tree in GraphViz .dot format. """
        dot = []
        dot.append ('strict digraph G {\n')
        self.root.to_dot (dot)
        dot.append ('}\n')
        return ''.join (dot)
