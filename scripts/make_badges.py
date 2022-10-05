#!python3

import glob
import re
import sys

from lxml import etree
import requests

DESTDIR="docs/" # physical
REFDIR="docs/"  # logical from .rst

# shields_io_colors = ["success", "important", "critical", "informational", "inactive"]

badges={}

# one build=passing badge for each python version
for filename in glob.glob(".tox/py3*/log/2-commands*.log"):
    with open (filename, "r") as fp:
        status = "passing"
        color = "success"
        for line in fp:
            if line.startswith("name: "):
                name = line[6:].strip()
            if line.startswith("==="):
                if m := re.search(r"(\d+) failed", line):
                    failed = int(m.group(1))
                    status = "failed"
                    color = "critical"
    badge = requests.get(f"https://img.shields.io/badge/{name}-{status}-{color}").text
    filename = f"_images/tox-{name}.svg"
    with open (f"{DESTDIR}{filename}", "w") as dest:
        dest.write(badge)

    badges[name]=f"{REFDIR}{filename}"

# one coverage badge
with open("htmlcov/index.html") as fp:
    root = etree.parse(fp, parser = etree.HTMLParser()).getroot()

coverage = root.xpath("//span[@class='pc_cov']")[0].text

cov = int (coverage.rstrip("%"))
if cov > 95:
    color = "success"
elif cov > 75:
    color = "important"
else:
    color = "critical"

badge = requests.get(f"https://img.shields.io/badge/coverage-{coverage}-{color}").text

filename = "_images/coverage.svg"
with open(f"{DESTDIR}{filename}", "w") as dest:
    dest.write(badge)
    badges["coverage"] = f"{REFDIR}{filename}"

# write a template to include in README.rst

with open (f"{DESTDIR}/badges.rst.include", "w") as dest:
    for name, filename in badges.items():
        dest.write(f".. |{name}| image:: {filename}\n\n")

    dest.write(" ".join(f"|{name}|" for name in badges) + "\n\n")
