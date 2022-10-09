""" Test the common substrings function. """

import pytest

from suffix_tree import Tree
from suffix_tree.builder_factory import BUILDERS


@pytest.mark.parametrize("builder", BUILDERS)
class TestCommonSubstrings:
    def test_common_substrings_repeats_1(self, builder):
        # [Gusfield1997]_ §7.6, 127ff
        tree = Tree(
            {
                "A": "sandollar",
                "B": "sandlot",
                "C": "handler",
                "D": "grand",
                "E": "pantry",
            }
        )
        result = []
        for k, length, path in tree.common_substrings():
            result.append((k, length, str(path)))

        assert result == [
            (2, 4, "s a n d"),
            (3, 3, "a n d"),
            (4, 3, "a n d"),
            (5, 2, "a n"),
        ]
