# -*- coding: utf-8 -*-
#

r"""Naive Tree Building Algorithm

A naive algorithm to build a suffix tree using :math:`\mathcal{O}(n^2)` time.

Credits: This implementation closely follows the description in [Gusfield1997]_
Chapter §5.4, page 93.

"""

from .util import Path, debug
from .node import Leaf

class Builder (object):
    """Builds the suffix-tree using a naive algorithm."""

    def __init__ (self, tree):
        self.tree = tree

    def add_string (self, the_id, the_path):
        """Add a string to the tree. """

        for i in range (0, the_path.end):
            path = Path (the_path.S, i, the_path.end)

            # find longest path from root
            node, matched_len, child = self.tree.find_path (path)

            # are we in the middle of an edge?
            if child is not None:
                node = node.split_edge (matched_len, child)

            assert matched_len == len (node), "Add String %d/%d" % (
                matched_len, len (node))

            if node.is_leaf ():
                assert matched_len == len (path)
                # In a generalized tree we may find a leaf is already there.  This
                # is not possible in a non-generalized tree because of the unique
                # ending character.
                node.add (the_id, Path (path.S, path.start, path.end))
                return node
            assert matched_len < len (path)
            new_leaf = Leaf (node, the_id, Path (path.S, path.start, path.end))
            assert path.S[path.start + matched_len] not in node.children # do not overwrite
            node.children[path.S[path.start + matched_len]] = new_leaf
            debug ('Adding %s to node %s as [%s]' % (str (new_leaf), str (node),
                                                     path.S[path.start + matched_len]))
        return new_leaf
