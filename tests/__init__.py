""" Package. Common stuff for tests. """

import pytest

from suffix_tree.builder_factory import BUILDERS

performance_test = pytest.mark.skipif(
    "not config.getoption('--performance')", reason="performance tests not requested"
)
""" @performance_test decorator

Skip the decorated test of not explicitly requested by commandline --performance.
"""
