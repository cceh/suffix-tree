#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

"""A Generalized Suffix-Tree.

This implementation:

- works with any python iterable, not just strings, if the items are hashable,
- values simplicity over speed,
- is a generalized suffix tree for sets of iterables ([Gusfield1997]_ §6.4),
- can convert the tree to .dot if the items convert to strings,

This implementation mostly follows [Gusfield1997]_ §6, with following differences:

- indices are 0-based (a Python convention),
- end indices point one element beyond the end (also a Python convention).

.. [Gusfield1997] Gusfield, Dan.  Algorithms on strings, trees, and sequences.
                  1997.  Cambridge University Press.

"""

import collections
import functools
import itertools
import sys

from . import lca_mixin

@functools.total_ordering
class UniqueEndChar (object):
    """ A singleton object to signal end of sequence. """
    def __str__ (self):
        return '$'
    def __lt__ (self, other):
        return False


_END = UniqueEndChar ()

DEBUG = 0

def debug (*a, **kw):
    """ Print a debug message to stderr. """

    if DEBUG:
        print (*a, file=sys.stderr, **kw)

class Pos (object):
    """ Represents a position in a string. """
    # pylint: disable=too-few-public-methods

    def __init__ (self, S, start = 0):
        assert 0 <= start <= len (S), "Pos: 0 <= %d <= %d" % (start, len (S))

        self.S     = S
        self.start = start

    def __str__ (self):
        return str (self.S[self.start])


class Path (object):
    """ A path in a suffix tree. """

    def __init__ (self, S, start = 0, end = None):
        if end is None:
            end = len (S)
        assert 0 <= start <= end <= len (S), "Path: 0 <= %d <= %d <= %d" % (start, end, len (S))

        self.S     = S
        self.start = start
        self.end   = end

    @classmethod
    def from_iterable (cls, iterable):
        """ Build a path froman iterable.

        Make the iterable immutable.
        """

        iterable = tuple (iterable)
        return Path (iterable, 0, len (iterable))

    def __str__ (self):
        return ' '.join ([str (o) for o in self.S[self.start:self.end]])

    def __len__ (self):
        return self.end - self.start

    def __lt__ (self, other):
        return self.S[self.start:self.end] < other.S[other.start:other.end]

    def compare (self, path, offset = 0):
        """ Compare a path against another. """
        length = min (len (self), len (path)) - offset
        offset1 = self.start + offset
        offset2 = path.start + offset
        i = 0

        while i < length:
            if self.S[offset1 + i] != path.S[offset2 + i]:
                break
            i += 1
        debug ("Comparing %s == %s at offset %d => %d" % (str (self), str (path), offset, i))
        return i


class Node (lca_mixin.Node):
    """The abstract base class for internal and leaf nodes.

    """

    def __init__ (self, path):
        super ().__init__ (path)

        self.path = path
        """One arbitrarily selected path that traverses this node. (Usually the first
        one in tree construction order.)
        """

        self.C = -1
        r"""For any internal node :math:`v` of :math:`\mathcal{T}`, define :math:`C(v)` to be the
        number of *distinct* string identifiers that appear at the leaves in the
        subtree of :math:`v`.  [Gusfield1997]_ §7.6, 127ff
        """

        self.is_left_diverse = None
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

        N.B. This being a generalized suffix tree, leafs *can be* left diverse,
        if the left characters in two strings are different or the leafs are at
        the beginning of the string.
        """

    def string_depth (self):
        """For any node :math:`v` in a suffix-tree, the *string-depth* of :math:`v` is
        the number of characters in :math:`v`'s label.  [Gusfield1997]_ §5.2, 90f
        """
        return len (self.path)

    def __str__ (self):
        raise NotImplementedError ()

    def is_leaf (self):
        """ Return True if the node is a leaf node. """
        raise NotImplementedError ()

    def compute_C (self):
        """ Calculate :math:`C(v)` numbers for all nodes. """
        raise NotImplementedError ()

    def compute_left_diverse (self):
        """ Calculate the left_diversity of this node. """
        raise NotImplementedError ()

    def pre_order (self, f):
        """ Walk the tree in visiting each node before its children. """
        raise NotImplementedError ()

    def post_order (self, f):
        """ Walk the tree in visiting each node after its children. """
        raise NotImplementedError ()

    def get_positions (self):
        """Get all paths that traverse this node."""

        paths = []
        def f (node):
            """ Helper """
            if node.is_leaf ():
                paths.extend (node.indices.items ())
        self.pre_order (f)
        return paths

    def maximal_repeats (self, a):
        """ Maximal repeats recursive function. """
        raise NotImplementedError ()

    def to_dot (self, a):
        """ Return node translated to Graphviz .dot format."""
        raise NotImplementedError ()


class Leaf (lca_mixin.Leaf, Node):
    """A leaf node.

    A suffix tree contains exactly len(S) leaf nodes.  A generalized suffix tree
    contains less than len (concat (S_1..S_N)) leaf nodes.

    """

    def __init__ (self, id_, path):
        super ().__init__ (path) # Node
        self.indices = {}
        self.add (id_, path)

    def __str__ (self):
        # start + 1 makes it Gusfield-compatible for easier comparing with examples in the book
        return ("^%s\n%s" % (str (self.path), super ().__str__ ()) +
                '\n'.join (['%s:%d' % (id_, path.start + 1) for id_,
                            path in self.indices.items ()]))

    def add (self, id_, path):
        """ Add a text id and suffix to the leaf node. """
        assert isinstance (path, Path)
        self.indices[id_] = path

    def is_leaf (self):
        return True

    def pre_order (self, f):
        f (self)
        return

    def post_order (self, f):
        f (self)
        return

    def compute_C (self):
        id_set = set (self.indices.keys ())
        self.C = len (id_set)
        return id_set

    def compute_left_diverse (self):
        """ See description in Node """
        left_characters = set ()
        for path in self.indices.values ():
            if path.start > 0:
                left_characters.add (path.S[path.start - 1])
            else:
                self.is_left_diverse = True
                return None
        self.is_left_diverse = len (left_characters) > 1
        return None if self.is_left_diverse else left_characters

    def maximal_repeats (self, a):
        if self.is_left_diverse:
            a.append ((self.C, self.path))

    def to_dot (self, a):
        a.append ('"%s" [color=green];\n' % str (self))


class Internal (lca_mixin.Internal, Node):
    """ An internal node.

    Internal nodes have at least 2 children.
    """

    def __init__ (self, path):
        super ().__init__ (path)
        self.children = {}
        """ A dictionary of item => node """

    def __str__ (self):
        return "^%s\n%s" % (str (self.path), super ().__str__ ())

    def is_leaf (self):
        return False

    def pre_order (self, f):
        f (self)
        for node in self.children.values ():
            node.pre_order (f)
        return

    def post_order (self, f):
        for node in self.children.values ():
            node.post_order (f)
        f (self)
        return

    def split_edge (self, new_len, node2):
        """Split edge

        Split self --> 2 into self --> new --> 2 and return the new node.
        new_len is the string-depth of the new node.

        """
        p1 = self.path
        p2 = node2.path
        assert len (p1) < new_len < len (p2), "split length %d->%d->%d" % (
            len (p1), new_len, len (p2))
        edge_start = p2.start + len (p1)
        edge_end   = p2.start + new_len
        new = Internal (Path (p2.S, p2.start, edge_end)) # it is always safe to shorten a path
        self.children[p2.S[edge_start]] = new     # substitute new node
        new.children  [p2.S[edge_end  ]] = node2

        debug ('Splitting %s:%s' % (str (self), str (node2)))
        debug ('Split Adding %s to node %s as [%s]' % (str (new), str (self), p2.S[edge_start]))

        return new

    def compute_C (self):
        id_set = set ()
        for node in self.children.values ():
            id_set.update (node.compute_C ())
        self.C = len (id_set)
        return id_set

    def compute_left_diverse (self):
        """ See description in Node """
        left_characters = set ()
        self.is_left_diverse = False
        for node in self.children.values ():
            lc = node.compute_left_diverse ()
            if lc is None:
                self.is_left_diverse = True
            else:
                left_characters.update (lc)
        if len (left_characters) > 1:
            self.is_left_diverse = True
        return None if self.is_left_diverse else left_characters

    def maximal_repeats (self, a):
        if self.is_left_diverse:
            a.append ((self.C, self.path))
        for child in self.children.values ():
            child.maximal_repeats (a)

    def to_dot (self, a):
        a.append ('"%s" [color=red];\n' % str (self))
        for node in self.children.values ():
            node.to_dot (a)
            p = node.path
            p = Path (p.S, p.start + self.string_depth (), p.start + node.string_depth ())
            a.append ('"%s" -> "%s" [label="%s"];\n' % (str (self), str (node), str (p)))


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

    """

    def __init__ (self, d):
        """ Initialize and build the tree from dict of iterables.

        """

        super ().__init__ (d)

        self.root = Internal (Path (tuple (), 0, 0))
        self.nodemap = dict ()
        """ map from string position to leaf node """

        for id_, S in d.items ():
            # input is any iterable, make an immutable copy and add a unique
            # character at the end
            path = Path.from_iterable (itertools.chain (S, [_END]))
            nodemap = self.nodemap[id_] = dict ()

            # build tree
            for i in range (0, path.end):
                nodemap[i] = self.add_string_naive (id_, Path (path.S, i, path.end))

    def to_dot (self):
        """ Output the tree in GraphViz .dot format. """
        dot = []
        dot.append ('strict digraph G {\n')
        self.root.to_dot (dot)
        dot.append ('}\n')
        return ''.join (dot)

    def find_path (self, path):
        """Find a path in the tree.

        Returns the deepest node on the path, the matched length of the path,
        and also the next deeper node if the matched length is longer than the
        string-depth of the deepest node on the path.

        """
        node = self.root
        matched_len = 0
        while matched_len < len (path):
            # find the edge to follow
            child = node.children.get (path.S[path.start + matched_len])
            if child:
                # follow the edge
                length = path.compare (child.path, matched_len)
                # there must be at least one match
                assert length > 0, "find_path length=%d matched_len=%d" % (length, matched_len)
                matched_len += length
                if matched_len < child.string_depth ():
                    # the path ends between node and child
                    return node, matched_len, child
                # we reached child, loop
                node = child
            else:
                # no edge to follow
                return node, matched_len, None
        # path exhausted
        return node, matched_len, None

    def add_string_naive (self, id_, path):
        r"""Add a string to the tree.

        A naive implementation using :math:`\mathcal{O}(n^2)` time with no
        optimizations.  See: [Gusfield1997]_ §5.4, 93

        Returns: the (new) leaf node
        """

        # find longest path from root
        node, matched_len, child = self.find_path (path)

        # are we in the middle of an edge?
        if child is not None:
            node = node.split_edge (matched_len, child)

        assert matched_len == node.string_depth (), "Add String %d/%d" % (
            matched_len, node.string_depth ())

        if node.is_leaf ():
            assert matched_len == len (path)
            # In a generalized tree we may find a leaf is already there.  This
            # is not possible in a non-generalized tree because of the unique
            # ending character.
            node.add (id_, Path (path.S, path.start, path.end))
            return node
        assert matched_len < len (path)
        new_leaf = Leaf (id_, Path (path.S, path.start, path.end))
        assert path.S[path.start + matched_len] not in node.children # do not overwrite
        node.children[path.S[path.start + matched_len]] = new_leaf
        debug ('Adding %s to node %s as [%s]' % (str (new_leaf), str (node),
                                                 path.S[path.start + matched_len]))
        return new_leaf

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
        1 a w y a w x a w x z $
        1 x a b x a c $
        2 a
        2 x
        2 x a
        2 $

        See [Gusfield1997]_ §7.12.1, 144ff.

        """
        a = []
        self.root.compute_C ()
        self.root.compute_left_diverse ()
        for child in self.root.children.values ():
            child.maximal_repeats (a)
        return a
