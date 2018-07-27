# -*- coding: utf-8 -*-
#

r"""Naive Tree Building Algorithm

A naive algorithm to build a suffix tree using :math:`\mathcal{O}(n^2)` time.

Credits: This implementation closely follows the description in [Gusfield1997]_
Chapter §5.4, page 93.

"""

from .util import Path, debug, debug_dot
from .node import Leaf
from . import builder

class Builder (builder.Builder):
    """Builds the suffix-tree using a naive algorithm."""

    def debug_dot (self, i):
        """ Write a debug graph. """
        debug_dot (self.tree, '/tmp/suffix_tree_naive_%s_%d' % (self.id, i))


    def build (self):
        """Add a string to the tree. """

        for i in range (0, self.path.end):
            path = Path (self.path.S, i, self.path.end)

            # find longest path from root
            node, matched_len, child = self.tree.find_path (path)

            # are we in the middle of an edge?
            if child is not None:
                node = node.split_edge (matched_len, child)

            assert matched_len == len (node), "Add String %d/%d" % (
                matched_len, len (node))

            assert matched_len < len (path)
            new_leaf = Leaf (node, self.id, Path (path.S, path.start, path.end))
            assert path.S[path.start + matched_len] not in node.children # do not overwrite
            node.children[path.S[path.start + matched_len]] = new_leaf
            debug ('Adding %s to node %s as [%s]',
                   str (new_leaf), str (node), path.S[path.start + matched_len])
            self.debug_dot (i)
