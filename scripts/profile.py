""" Profile the builder. """

# pylint: disable=missing-docstring

import cProfile
import random
import sys

from suffix_tree import Tree
from suffix_tree import builder_factory

random.seed(42)

SIZE = 100_000
SYMBOLS = "".join(random.choices("ACTG", k=SIZE))


def profiler(sequence):
    tree = Tree()
    tree.add("A", sequence, builder=sys.argv[1])


cProfile.runctx("profiler(SYMBOLS)", globals(), locals())
