#!/usr/bin/python3

"""Sample the time complexity for all the builders."""

import gc
import json
import random
import time
from typing import Tuple, List, Dict

import numpy as np

from suffix_tree import Tree
from suffix_tree.util import Symbols
from suffix_tree.builder_factory import BUILDERS, builder_factory


SIZE = 10_000_000
# SIZE = 1_000_000
TICK = SIZE // 10
WORDLIST = "/usr/share/dict/words"
random.seed(42)

SOURCES: Dict[str, Symbols] = {}
SOURCES["4ACGT"] = "".join(random.choices("ACTG", k=SIZE))
SOURCES["20PROT"] = "".join(random.choices("ARNDCQEGHILKMFPSTWYV", k=SIZE))
SOURCES["1000INT"] = random.choices(range(1000), k=SIZE)

try:
    # ~ 100_000 words
    with open(WORDLIST, "r") as fp:
        WORDS = [line.strip() for line in fp]
    words = ""
    while len(words) < SIZE:
        words += " ".join(random.choices(WORDS, k=10000))
    SOURCES["WORDLIST"] = words[0:SIZE]
except FileNotFoundError:
    print("No wordlist found")


def timer(builder, sequence: Symbols) -> List[Tuple[int, float]]:  # phase, seconds
    print(f"Building {id_} with {builder.name}")
    tree = Tree()
    elapsed = []
    start = time.process_time()
    builder.set_progress_function(
        TICK, lambda i: elapsed.append((i, time.process_time() - start))
    )
    tree.add(
        "A",
        sequence,
        builder=builder,
    )
    return elapsed


jso = []
gc.disable()
for id_, symbols in SOURCES.items():
    for builder_ in BUILDERS:
        builder = builder_factory(builder_)()
        elapsed = timer(builder, symbols)
        gc.collect()

        jso.append(
            {
                "source": id_,
                "builder": builder.name,
                "xdata": [x[0] for x in elapsed],
                "ydata": [x[1] for x in elapsed],
            }
        )

with open("graph_time_complexity.json", "w") as fp:
    json.dump(jso, fp, indent=2)
