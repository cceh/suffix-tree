""" Profile the builder. """

# pylint: disable=missing-docstring

import random

import cProfile

from suffix_tree import Tree

SIZE = 100_000
SYMBOLS = "".join(random.choices("ACTG", k=SIZE))


def profiler(sequence):
    tree = Tree()
    tree.add("A", sequence)


cProfile.runctx("profiler(SYMBOLS)", globals(), locals())
