#!/usr/bin/python3

"""Build a graph of time complexity for all the builders."""

import itertools
import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as optimize

SOURCES = {
    "4ACGT": "Random Choice of 4 Symbols",
    "20PROT": "Random Choice of 20 Symbols",
    "1000INT": "Random Choice of 1000 Symbols",
    "WORDLIST": "Random Choice of English Words, concatenated",
}

BUILDERS = {
    "Naive": "r",
    "Ukkonen": "g",
    "Gusfield": "b",
}


def func(x, b, c):
    return b * x + c * x * x


def print_fit(b, c):
    f = []
    if c > 1e-10:
        f.append(f"{c:.3g}x²")
    if b > 1e-10:
        f.append(f"{b:.3g}x")
    return "+".join(f)


fn = sys.argv[1]

with open(fn, "r") as fp:
    jso = json.load(fp)

plt.rcParams["figure.figsize"] = (20, 20)
with plt.style.context("bmh"):
    fig, axs = plt.subplots(nrows=2, ncols=2, tight_layout=True)
    i = 0
    for source, group in itertools.groupby(jso, key=lambda x: x["source"]):
        title = SOURCES[source]
        ax = axs.flat[i]
        i += 1
        for data in group:
            xdata = np.array(data["xdata"])
            ydata = np.array(data["ydata"])
            builder = data["builder"]
            color = BUILDERS[builder]

            pxdata = xdata / 1e6
            ax.plot(pxdata, ydata, "o", color=color)

            # fit to a quadratic curve
            opt, pcov = optimize.curve_fit(
                func, pxdata, ydata, bounds=((0, 0), (np.inf, np.inf))
            )

            ax.plot(
                pxdata,
                func(pxdata, *opt),
                "--",
                color=color,
                label=f"{builder} fit = {print_fit(*opt)}",
            )

            ax.set_title(title, fontsize=12)
            ax.set_xlabel("Sequence Length (×10^6)", fontsize=10)
            ax.set_ylabel("Time Elapsed (s)", fontsize=10)
            ax.legend(loc="upper left")

plt.savefig("graph_time_complexity.png")
plt.show()
