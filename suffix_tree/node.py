# -*- coding: utf-8 -*-
#

"""A node class for a Generalized Suffix Tree"""

from .util import Path
from . import lca_mixin

class Node (lca_mixin.Node):
    """The abstract base class for internal and leaf nodes.

    """

    def __init__ (self, parent, path, **kw):
        super ().__init__ (parent, path, **kw)

        self.parent = parent
        """ The parent if this node.  Used by Ukkonen and LCA. """

        self.suffix_link = None
        """ Used by the Ukkonen algorithm while constructing the tree. """

        self.path = path
        """One arbitrarily selected path that traverses this node. (Usually the first
        one in tree construction order.)
        """

        self.name = kw.get ('name', '')
        """ A name can be given to the node for easier debugging. """

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
        return len (self)

    def edge_len (self):
        """The length of the edge going into the node."""
        if self.parent is not None:
            return len (self) - len (self.parent)
        return len (self)

    def edge (self):
        """The edge going into this node."""
        if self.parent is not None:
            return Path (self.path.S, self.path.end - self.edge_len (), self.path.end)
        return Path (tuple (), 0, 0)

    def __str__ (self):
        raise NotImplementedError ()

    def __len__ (self):
        """ We define the length of a node as its string depth. """
        return len (self.path)

    def is_leaf (self): # pylint: disable=no-self-use
        """ Return True if the node is a leaf node. """
        return False

    def is_internal (self):  # pylint: disable=no-self-use
        """ Return True if the node is an internal node. """
        return False

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

    def find_path (self, path):
        """Find a path starting from this node.

        The path is absolute.

        Returns the deepest node on the path, the matched length of the path,
        and also the next deeper node if the matched length is longer than the
        string-depth of the deepest node on the path.

        """
        node = self
        matched_len = len (node)
        while matched_len < len (path):
            # find the edge to follow
            child = node.children.get (path.S[path.start + matched_len]) # pylint: disable=no-member
            if child:
                # follow the edge
                length = path.compare (child.path, matched_len)
                # there must be at least one match
                assert length > 0, "find_path length=%d matched_len=%d" % (length, matched_len)
                matched_len += length
                if matched_len < len (child):
                    # the path ends between node and child
                    return node, matched_len, child
                # we reached child, loop
                node = child
            else:
                # no edge to follow
                return node, matched_len, None
        # path exhausted
        return node, matched_len, None

    def get_positions (self):
        """Get all paths that traverse this node."""

        paths = []
        def f (node):
            """ Helper """
            if node.is_leaf ():
                paths.append ((node.strid, node.path))
        self.pre_order (f)
        return paths

    def maximal_repeats (self, a):
        """ Maximal repeats recursive function. """
        raise NotImplementedError ()

    def to_dot (self, a):
        """ Return node translated to Graphviz .dot format."""
        if self.suffix_link is not None:
            a.append ('"%s" -> "%s" [color=blue; constraint=false];\n'
                      % (str (self), str (self.suffix_link)))


class Leaf (lca_mixin.Leaf, Node):
    """A leaf node.

    A suffix tree contains exactly len(S) leaf nodes.  A generalized suffix tree
    contains less than len (concat (S_1..S_N)) leaf nodes.

    """

    def __init__ (self, parent, strid, path, **kw):
        super ().__init__ (parent, path, **kw) # Node
        self.strid = strid

    def __str__ (self):
        # start + 1 makes it Gusfield-compatible for easier comparing with examples in the book
        return ("%s%s" % (self.name or str (self.path), super ().__str__ ())
                + ' %s:%d' % (self.strid, self.path.start + 1))

    def is_leaf (self):
        return True

    def pre_order (self, f):
        f (self)
        return

    def post_order (self, f):
        f (self)
        return

    def compute_C (self):
        self.C = 1
        return set (self.strid)

    def compute_left_diverse (self):
        """ See description in Node """
        left_characters = set ()
        if self.path.start > 0:
            left_characters.add (self.path.S[self.path.start - 1])
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
        super ().to_dot (a)


class Internal (lca_mixin.Internal, Node):
    """ An internal node.

    Internal nodes have at least 2 children.
    """

    def __init__ (self, parent, path, **kw):
        super ().__init__ (parent, path, **kw)
        self.children = {}
        """ A dictionary of item => node """

    def __str__ (self):
        return "%s%s" % (self.name or (str (self.path)), super ().__str__ ())

    def is_internal (self):
        return True

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

    def split_edge (self, new_len, child):
        """Split edge

        Split self --> child into self --> new_node --> child and return the new node.
        new_len is the string-depth of the new node.

        """
        p1 = self.path
        p2 = child.path
        assert len (p1) < new_len < len (p2), "split length %d->%d->%d" % (
            len (p1), new_len, len (p2))
        edge_start = p2.start + len (p1)
        edge_end   = p2.start + new_len
        # it is always safe to shorten a path
        new_node = Internal (self, Path (p2.S, p2.start, edge_end))

        self.children[p2.S[edge_start]] = new_node     # substitute new node
        new_node.children [p2.S[edge_end  ]] = child
        child.parent = new_node

        # debug ('Splitting %s:%s', str (self), str (child))
        # debug ('Split Adding %s to node %s as [%s]',
        #        str (new_node), str (self), p2.S[edge_start])

        return new_node

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
        super ().to_dot (a)
        for key in sorted (self.children):
            child = self.children[key]
            a.append ('"%s" -> "%s" [label="%s"];\n' % (str (self), str (child), str (key)))
            child.to_dot (a)
