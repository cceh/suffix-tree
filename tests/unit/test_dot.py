""" Test the to_dot ()  method. """

import pytest

from suffix_tree import Tree, util
from suffix_tree.tree import BUILDERS


@pytest.fixture(scope="module")
def debug_mode():
    util.DEBUG_DOT = True
    yield True
    util.DEBUG_DOT = False


@pytest.mark.parametrize("builder", BUILDERS)
class TestFind:
    def progress(self, i):
        return

    def test_to_dot(self, builder, tmp_path):
        tree = Tree({"A": "abcde"}, builder=builder, progress=self.progress)
        if util.is_debug():
            util.debug_dot(tree, tmp_path / "suffix_tree")

    def test_to_dot_debug(self, builder, tmp_path, debug_mode):
        tree = Tree({"A": "abcde"}, builder=builder, progress=self.progress)
        if util.is_debug():
            util.debug_dot(tree, tmp_path / "suffix_tree")
