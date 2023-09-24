""" Test the Ukkonen "online" builder. """

# pylint: disable=missing-docstring

import pytest

from suffix_tree import Tree
from suffix_tree.builder_factory import BUILDERS


class TestOnline:
    def test_online(self):
        """Test building Ukkonen from an iterator."""
        tree = Tree()

        def generator():
            yield from "xabxac"
            assert tree.find("xac")  # tree is always ready
            yield from "abc"

        tree.add("A", generator(), builder="ukkonen")
        assert tree.find("xacabc")
