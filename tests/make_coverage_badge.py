#!python3

import json
import sys

import requests

# shields_io_colors = ["success", "important", "critical", "informational", "inactive"]

if __name__ == "__main__":
    j = json.load(sys.stdin)
    coverage = j["totals"]["percent_covered_display"]

    cov = int(coverage)
    if cov > 95:
        color = "success"
    elif cov > 75:
        color = "important"
    else:
        color = "critical"

    print(requests.get(
        f"https://img.shields.io/badge/coverage-{cov}%-{color}"
    ).text)
