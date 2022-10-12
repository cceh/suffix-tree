""" Other tests. """

import pytest

from suffix_tree.util import Path


class TestPath:
    def test_path_subscript(self):
        path = Path("abc")
        assert path[0] == "a"
        assert path[2] == "c"
