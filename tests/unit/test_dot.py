""" Test the to_dot () method. """

import pytest

from suffix_tree import Tree, util
from suffix_tree.builder_factory import BUILDERS, builder_factory


@pytest.mark.parametrize("builder", BUILDERS)
class TestToDot:
    def progress(self, i):
        return

    def test_to_dot(self, builder, tmp_path):
        builder = builder_factory(builder)()
        builder.set_progress_function(1, self.progress)
        tree = Tree({"A": "abcde"}, builder=builder)
        tree.root.debug_dot(tmp_path / "suffix_tree.dot")

    def test_to_dot_debug(self, builder, tmp_path, debug_dot_mode):
        builder = builder_factory(builder)()
        builder.set_progress_function(1, self.progress)
        tree = Tree()
        tree.add("A", "abcde", builder=builder)
        if util.is_debug():
            tree.root.debug_dot(tmp_path / "suffix_tree.dot")
