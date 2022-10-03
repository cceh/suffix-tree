import argparse

import pytest

from suffix_tree import Tree, util


@pytest.fixture
def tree():
    """A small tree for testing."""
    return Tree(
        {
            "A": "abcde",
            "B": "bcde",
            "C": "cde",
            "D": "de",
            "E": "e",
        }
    )

class DebugAction(argparse.BooleanOptionalAction):
    """This action turns on the DEBUG flags so we can test the debug code."""
    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            util.DEBUG = True
            util.DEBUG_LABELS = True
            # do not turn on DEBUG_DOT, it would run too slow. we test it in test_dot


def pytest_addoption(parser):
    parser.addoption(
        "--performance", action="store_true", help="run performance tests"
    )
    parser.addoption(
        "--debug-mode", action=DebugAction, help="turn on DEBUG mode while testing"
    )
