import argparse
import sys

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

@pytest.fixture()
def debug_dot_mode():
    """This fixture turns on debug dot mode."""
    util.DEBUG_DOT = True
    yield True
    util.DEBUG_DOT = False


if sys.version_info >= (3,9):
    class DebugAction(argparse.BooleanOptionalAction):
        """This action turns on the DEBUG flags so we get coverage of the debug code."""
        def __call__(self, parser, namespace, values, option_string=None):
            if option_string in self.option_strings:
                util.DEBUG = True
                util.DEBUG_LABELS = True
                # do not turn on DEBUG_DOT, it would run too slow. we test it in test_dot
else:
    class DebugAction(argparse.Action):
        """This action turns on the DEBUG flags so we get coverage of the debug code."""
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super().__init__(option_strings, dest, **kwargs)
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
