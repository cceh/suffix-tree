#!/usr/bin/python3

"""Sample the time complexity for all the builders."""

import gc
import json
import random
import time

import numpy as np

from suffix_tree import Tree
from suffix_tree.util import Symbols
from suffix_tree.test.tests import BUILDERS


SIZE = 10_000_000
# SIZE = 100_000
STEPS = 20
WORDLIST = "/usr/share/dict/words"
random.seed(42)

SOURCES: dict[str, Symbols] = {}
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


def timer(builder, sequence: Symbols) -> list[float]:  # in seconds
    tree = Tree()
    elapsed = []
    start = time.process_time()
    tree.add(
        "A",
        sequence,
        builder=builder,
        progress=lambda x: elapsed.append(time.process_time() - start),
    )
    elapsed.append(time.process_time() - start)
    return elapsed


jso = []
xdata = np.linspace(0, SIZE, STEPS + 1, dtype=int)
gc.disable()
for id_, symbols in SOURCES.items():
    for builder in BUILDERS:
        print(f"Building {id_} with {builder.name}")
        ydata = np.array(timer(builder, symbols)).take(xdata)
        gc.collect()

        jso.append(
            {
                "source": id_,
                "builder": builder.name,
                "xdata": xdata.tolist(),
                "ydata": ydata.tolist(),
            }
        )

with open("graph_time_complexity.json", "w") as fp:
    json.dump(jso, fp, indent=2)
