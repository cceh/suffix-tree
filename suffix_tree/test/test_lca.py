""" Test the Least Common Ancestor (LCA) implementation. """

# pylint: disable=missing-docstring

import unittest

from parameterized import parameterized

from suffix_tree import Tree
from .tests import BUILDERS

class TestLCA (unittest.TestCase):

    @parameterized.expand(BUILDERS)
    def test_lca (self, _, builder):
        tree = Tree ({ 'A' : 'xabxac', 'B' : 'awyawxawxz' }, builder = builder)
        tree.prepare_lca ()
        self.assertEqual (tree.lca (tree.nodemap['A'][1], tree.nodemap['B'][3]).lca_id,  8)
        self.assertEqual (tree.lca (tree.nodemap['A'][0], tree.nodemap['B'][8]).lca_id,  2)
        self.assertEqual (tree.lca (tree.nodemap['B'][1], tree.nodemap['B'][7]).lca_id, 19)
        self.assertEqual (tree.lca (tree.nodemap['A'][0], tree.nodemap['B'][7]).lca_id,  1)


if __name__ == '__main__':
    unittest.main ()
