""" Test the find ()  method. """

# pylint: disable=missing-docstring

import pytest

from suffix_tree import Tree
from suffix_tree.builder_factory import BUILDERS


@pytest.mark.parametrize("builder", BUILDERS)
class TestFind:
    def test_find_1(self, builder):
        # Gusfield1997 Figure 5.1 Page  91
        tree = Tree({"A": "xabxac"}, builder=builder)
        assert tree.find("x")
        assert tree.find("xa")
        assert tree.find("xab")
        assert tree.find("xabx")
        assert tree.find("xabxa")
        assert tree.find("xabxac")

        assert not tree.find("xabxacx")

        assert tree.find("abxac")
        assert tree.find("bxac")
        assert tree.find("xac")
        assert tree.find("ac")
        assert tree.find("c")

        assert not tree.find("d")
        assert not tree.find("xx")
        assert not tree.find("xabxaa")

    def test_find_2(self, builder):
        # Gusfield1997 Figure 5.2 Page  92
        tree = Tree({"A": "awyawxawxz"}, builder=builder)
        assert tree.find("awx")
        assert tree.find("awy")
        assert not tree.find("awz")

    def test_find_3(self, builder):
        # Gusfield1997 Figure 7.1 Page 129
        tree = Tree({"A": "xyxaxaxa"}, builder=builder)
        assert tree.find("xyxaxaxa")
        assert tree.find("xax")
        assert tree.find("axa")
        assert not tree.find("ay")

    def test_find_4(self, builder):
        tree = Tree(
            {
                "A": (
                    "232 020b 092 093 039 061 102 135 098 099 "
                    "039 040 039 040 044 141 140 098"
                ).split(),
                "B": "097 098 039 040 041 129 043".split(),
                "C": (
                    "097 098 039 040 020a 022 023 097 095 094 098 "
                    "043 044 112 039 020b 039 098"
                ).split(),
            },
            builder=builder,
        )
        assert tree.find("039 040 041".split())
        assert tree.find("039 040 039 040".split())
        assert tree.find("020a 022 023".split())
        assert tree.find("232 020b 092".split())
        assert tree.find("097 098 039 040".split())
        assert tree.find("141 140 098".split())
        assert not tree.find("039 040 042".split())

    def test_find_5(self, builder):
        tree = Tree(
            {
                "A": "aaaaa",
                "B": "bbbb",
                "C": "ccc",
                "D": "dd",
                "E": "e",
            },
            builder=builder,
        )
        assert len(tree.find_all("a")) == 5
        assert len(tree.find_all("b")) == 4
        assert len(tree.find_all("c")) == 3
        assert len(tree.find_all("d")) == 2
        assert len(tree.find_all("e")) == 1
        assert len(tree.find_all("f")) == 0
        assert tree.find_all("a")[0][0] == "A"
        assert tree.find_all("b")[0][0] == "B"

    def test_find_6(self, builder):
        tree = Tree(
            {
                "A": "a",
                "B": "ab",
                "C": "abc",
                "D": "abcd",
                "E": "abcde",
            },
            builder=builder,
        )
        assert len(tree.find_all("abcde")) == 1
        assert len(tree.find_all("abcd")) == 2
        assert len(tree.find_all("abc")) == 3
        assert len(tree.find_all("ab")) == 4
        assert len(tree.find_all("a")) == 5

    def test_find_7(self, builder):
        tree = Tree(
            {
                "A": "abcde",
                "B": "bcde",
                "C": "cde",
                "D": "de",
                "E": "e",
            },
            builder=builder,
        )
        assert len(tree.find_all("abcde")) == 1
        assert len(tree.find_all("bcde")) == 2
        assert len(tree.find_all("cde")) == 3
        assert len(tree.find_all("de")) == 4
        assert len(tree.find_all("e")) == 5

    def test_find_8(self, builder):
        tree = Tree({"A": "xabxac", "B": "awyawxawxz"}, builder=builder)
        assert tree.find_id("A", "abx")
        assert tree.find_id("B", "awx")
        assert not tree.find_id("B", "abx")
