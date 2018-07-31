import setuptools

VERSION="0.0.6"

with open ("README.rst", "r") as fh:
    long_description = fh.read ()

setuptools.setup (
    name="suffix-tree",
    version=VERSION,
    author="Marcello Perathoner",
    author_email="marcello@perathoner.de",
    description="A Generalized Suffix Tree for any iterable, with Lowest Common Ancestor retrieval",
    keywords=['suffix', 'tree', 'suffixtree', 'ukkonen', 'gusfield', 'lca'],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/cceh/suffix-tree",
    packages=setuptools.find_packages (),
    # See: https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Text Processing :: Linguistic",
    ),
)
