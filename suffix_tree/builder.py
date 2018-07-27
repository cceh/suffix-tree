# -*- coding: utf-8 -*-
#

"""Builder Base

"""

from .util import Path


class Builder (object):
    """Base class for all builders."""

    def __init__ (self, tree, id_, path):
        self.tree = tree
        self.id   = id_
        self.path = path
        self.root = tree.root


    def fixup_e (self, M):
        """ Fixup :math:`e` on all leaves.

        For Ukkonen-style builders.
        """

        def f (node):
            """ helper """
            if node.is_leaf ():
                # Turn the variable :math:`e` into a constant because
                # the next string added will use :math:`e` again.
                # pylint: disable=protected-access
                if node.path._end == Path.inf:
                    node.path._end = M

        self.tree.root.pre_order (f)
