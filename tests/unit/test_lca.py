""" Test the Least Common Ancestor (LCA) implementation. """

# pylint: disable=missing-docstring

import pytest

from suffix_tree import Tree
from suffix_tree.builder_factory import BUILDERS


@pytest.mark.parametrize("builder", BUILDERS)
class TestLCA:
    def test_lca(self, builder):
        tree = Tree({"A": "xabxac", "B": "awyawxawxz"}, builder=builder)
        tree.prepare_lca()
        assert tree.lca(tree.nodemap["A"][1], tree.nodemap["B"][3]).lca_id == 8
        assert tree.lca(tree.nodemap["B"][3], tree.nodemap["A"][1]).lca_id == 8

        assert tree.lca(tree.nodemap["A"][0], tree.nodemap["B"][8]).lca_id == 2
        assert tree.lca(tree.nodemap["B"][8], tree.nodemap["A"][0]).lca_id == 2

        assert tree.lca(tree.nodemap["B"][1], tree.nodemap["B"][7]).lca_id == 19
        assert tree.lca(tree.nodemap["B"][7], tree.nodemap["B"][1]).lca_id == 19

        assert tree.lca(tree.nodemap["A"][0], tree.nodemap["B"][7]).lca_id == 1
        assert tree.lca(tree.nodemap["B"][7], tree.nodemap["A"][0]).lca_id == 1

        assert (
            tree.lca(tree.nodemap["A"][1], tree.nodemap["A"][1]) == tree.nodemap["A"][1]
        )
