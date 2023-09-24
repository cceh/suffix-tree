""" Test the to_dot () method and other spurious things. """

import pytest

from suffix_tree.builder_factory import builder_factory
from suffix_tree import naive, ukkonen, mccreight


class TestBuilderFactory:
    def test_builder_factory(self):
        assert builder_factory("mccreight") == mccreight.Builder
        assert builder_factory("ukkonen") == ukkonen.Builder
        assert builder_factory("naive") == naive.Builder
        assert builder_factory("foo") == mccreight.Builder
        assert builder_factory() == mccreight.Builder
