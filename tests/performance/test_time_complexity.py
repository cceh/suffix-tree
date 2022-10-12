""" Test the find ()  method. """

# pylint: disable=missing-docstring

import itertools
import gc
import random
import time
from typing import Optional, List, Tuple

# import cProfile

import pytest

from suffix_tree import Tree, util
from suffix_tree.builder_factory import BUILDERS
from .. import performance_test

SIZE = 16_000
TICK = 1_000
FACTORS = [16, 8, 4, 2, 1]
FUZZ = 1.2
WORDLIST = "/usr/share/dict/words"

SYMBOLS = "".join(random.choices("ACTG", k=SIZE))

WORDS: Optional[List[str]] = None
try:
    # ~ 100_000 words
    with open(WORDLIST, "r") as fp:
        words = [line.strip().replace("'s", "") for line in fp]
    random.seed(42)
    WORDS = random.choices(words, k=SIZE // 10)
except FileNotFoundError:
    pass


def print_elapsed(elapsed):
    f = 1e9
    s = "elapsed: "
    for e in elapsed:
        s += f" {e / f:.2f}"
    print(s)


def pairwise(iterable):
    # python3.10 has this in itertools
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def assert_elapsed(elapsed):
    for e1, e2 in pairwise(elapsed):
        # give some leeway to account for cache fluctuations
        assert FUZZ * e1 > e2


@pytest.mark.parametrize("builder", BUILDERS)
@performance_test
class TestTimeComplexity:
    """Tests for (almost) linear time complexity.

    These tests are finicky if the machine is loaded.  Better not run them under CI.
    """

    def test_time_string_length(self, builder):
        """Test single string insertions.

        This test inserts a long string into the tree.
        """

        if util.is_debug():
            pytest.skip("debug mode is not linear")
        print(f"\ntesting {builder.name}")
        gc.disable()

        def timer(sequence) -> List[Tuple[int, float]]:
            tree = Tree()
            elapsed = []
            start: float = time.process_time()
            builder.set_progress_function(
                TICK, lambda i: elapsed.append((i, time.process_time() - start))
            )
            tree.add(
                "A",
                sequence,
                builder=builder,
            )
            return elapsed

        # cProfile.runctx("timer(CHARS)", globals(), locals())
        t = timer(SYMBOLS)
        SIZE = len(SYMBOLS)
        elapsed = [f * t[SIZE // f - 1] for f in FACTORS]

        print_elapsed(elapsed)

        if builder.name == "Naive":
            pytest.skip("The Naive builder is not expected to work in linear time.")

        assert_elapsed(elapsed)

        gc.collect()
        gc.enable()

    def test_time_string_count(self, builder):
        """Test multiple string insertions.

        This test inserts lots of short strings into the tree.  As a result the tree
        will not grow very deep and even the Naive builder will perform well.
        """

        if util.is_debug():
            pytest.skip("debug mode is not linear")
        if WORDS is None:
            pytest.skip(f"no wordlist in {WORDLIST}")

        print(f"\ntesting {builder.name}")
        gc.disable()

        tree = Tree()
        start = time.process_time_ns()

        def timer(id_, sequence) -> int:
            tree.add(id_, sequence, builder=builder)
            return time.process_time_ns() - start

        t = [timer(n, word) for n, word in enumerate(WORDS)]
        SIZE = len(WORDS)
        elapsed = [f * t[SIZE // f - 1] for f in FACTORS]

        print_elapsed(elapsed)
        assert_elapsed(elapsed)

        gc.collect()
        gc.enable()
