""" Test the pre- and post_order tree walkes. """


class TestPrePostOrder:
    def leaf_count(self, node):
        if node.is_leaf():
            self.count += 1

    def test_preorder(self, tree):
        self.count = 0
        tree.pre_order(self.leaf_count)
        assert self.count == 20

    def test_postorder(self, tree):
        self.count = 0
        tree.post_order(self.leaf_count)
        assert self.count == 20
